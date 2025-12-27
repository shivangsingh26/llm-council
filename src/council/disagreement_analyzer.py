"""
Disagreement Analyzer: Quantifies council agreement levels.

Calculates a 0.0-1.0 disagreement score based on:
1. Semantic similarity of answers (70% weight)
2. Confidence variance (30% weight)

Low score (< 0.3) = High agreement → Fast path
High score (> 0.7) = High disagreement → Deep path
"""

import numpy as np
from typing import Dict, List, Tuple
from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import os
import logging
from dotenv import load_dotenv

from src.models.schemas import ResearchResponse, ConfidenceLevel

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DisagreementAnalyzer:
    """
    Analyzes council responses to determine agreement level.

    Uses:
    - OpenAI embeddings (text-embedding-3-small) for semantic similarity
    - Statistical variance for confidence spread
    - Weighted combination (70% semantic, 30% confidence)
    """

    # Model configuration
    EMBEDDING_MODEL = "text-embedding-3-small"

    # Weights for final score
    SEMANTIC_WEIGHT = 0.7
    CONFIDENCE_WEIGHT = 0.3

    # Confidence level mapping
    CONFIDENCE_MAP = {
        ConfidenceLevel.LOW: 0.25,
        ConfidenceLevel.MEDIUM: 0.50,
        ConfidenceLevel.HIGH: 0.75,
        ConfidenceLevel.VERY_HIGH: 0.95
    }

    def __init__(self):
        """Initialize with OpenAI client for embeddings."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.openai_client = AsyncOpenAI(api_key=api_key)

    async def calculate_disagreement(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> Dict:
        """
        Calculate disagreement score for council responses.

        Args:
            responses: Dict mapping model names to their responses

        Returns:
            Dict with:
                - score: float (0.0-1.0 combined disagreement score)
                - semantic_disagreement: float
                - confidence_variance: float
                - explanation: str
                - details: Dict with pairwise similarities and confidence levels

        Raises:
            ValueError: If fewer than 2 responses provided
        """
        if len(responses) < 2:
            raise ValueError("Need at least 2 responses to calculate disagreement")

        logger.info(f"Calculating disagreement for {len(responses)} council responses")

        # Step 1: Extract claims from all responses
        claims = self._extract_claims(responses)

        # Step 2: Get embeddings for semantic comparison
        embeddings = await self._get_embeddings(claims)

        # Step 3: Calculate pairwise similarities
        similarities, pairwise_details = self._pairwise_similarities(embeddings)
        avg_similarity = np.mean(similarities)
        semantic_disagreement = 1.0 - avg_similarity

        # Step 4: Calculate confidence variance
        confidence_variance = self._calculate_confidence_variance(responses)

        # Step 5: Combine into final score (weighted)
        final_score = (
            self.SEMANTIC_WEIGHT * semantic_disagreement +
            self.CONFIDENCE_WEIGHT * confidence_variance
        )
        final_score = np.clip(final_score, 0.0, 1.0)

        # Step 6: Generate explanation
        explanation = self._generate_explanation(
            final_score, semantic_disagreement, confidence_variance, responses
        )

        # Step 7: Build details
        details = {
            "pairwise_similarities": pairwise_details,
            "confidence_levels": {
                name: self._confidence_to_float(resp.confidence)
                for name, resp in responses.items()
            },
            "key_point_overlap": self._calculate_key_point_overlap(responses)
        }

        result = {
            "score": float(final_score),
            "semantic_disagreement": float(semantic_disagreement),
            "confidence_variance": float(confidence_variance),
            "explanation": explanation,
            "details": details
        }

        logger.info(f"Disagreement analysis complete: score={final_score:.3f}, explanation={explanation}")

        return result

    def _extract_claims(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> Dict[str, str]:
        """
        Extract claims from each response for comparison.

        Combines answer + key points into single text.
        """
        claims = {}

        for model_name, response in responses.items():
            # Combine main answer with key points
            text_parts = [response.answer]

            if response.key_points:
                text_parts.extend(response.key_points)

            claims[model_name] = "\n".join(text_parts)

        return claims

    async def _get_embeddings(
        self,
        texts: Dict[str, str]
    ) -> Dict[str, List[float]]:
        """
        Get embeddings for all texts using OpenAI API.

        Uses text-embedding-3-small for cost efficiency (~$0.00002/1k tokens).
        """
        embeddings = {}

        for model_name, text in texts.items():
            try:
                response = await self.openai_client.embeddings.create(
                    model=self.EMBEDDING_MODEL,
                    input=text
                )
                embeddings[model_name] = response.data[0].embedding
                logger.debug(f"Generated embedding for {model_name}: {len(response.data[0].embedding)} dimensions")
            except Exception as e:
                logger.error(f"Failed to get embedding for {model_name}: {e}")
                # Use zero vector as fallback (will show as complete disagreement)
                embeddings[model_name] = [0.0] * 1536

        return embeddings

    def _pairwise_similarities(
        self,
        embeddings: Dict[str, List[float]]
    ) -> Tuple[List[float], Dict[str, Dict[str, float]]]:
        """
        Calculate cosine similarity between all pairs.

        Returns:
            - List of similarity scores (for averaging)
            - Dict of pairwise details (for reporting)
        """
        model_names = list(embeddings.keys())
        similarities = []

        # Initialize pairwise_details for all models first
        pairwise_details = {model: {} for model in model_names}

        for i, model1 in enumerate(model_names):
            for j, model2 in enumerate(model_names):
                if i < j:  # Only calculate each pair once
                    emb1 = np.array(embeddings[model1]).reshape(1, -1)
                    emb2 = np.array(embeddings[model2]).reshape(1, -1)

                    similarity = cosine_similarity(emb1, emb2)[0][0]
                    similarities.append(similarity)

                    # Store bidirectionally
                    pairwise_details[model1][model2] = float(similarity)
                    pairwise_details[model2][model1] = float(similarity)

                    logger.debug(f"Similarity {model1} <-> {model2}: {similarity:.3f}")

        return similarities, pairwise_details

    def _calculate_confidence_variance(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> float:
        """Calculate variance in confidence levels across models."""
        confidences = [
            self.CONFIDENCE_MAP[response.confidence]
            for response in responses.values()
        ]

        variance = float(np.var(confidences))
        logger.debug(f"Confidence variance: {variance:.3f}")

        return variance

    def _calculate_key_point_overlap(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> float:
        """
        Calculate overlap in key points (simple Jaccard similarity).

        Returns 0.0-1.0 score.
        """
        if not any(r.key_points for r in responses.values()):
            return 1.0  # No key points = assume agreement

        # Get all key points as sets
        key_point_sets = [
            set(resp.key_points) if resp.key_points else set()
            for resp in responses.values()
        ]

        # Calculate pairwise Jaccard similarities
        similarities = []
        for i in range(len(key_point_sets)):
            for j in range(i + 1, len(key_point_sets)):
                set1, set2 = key_point_sets[i], key_point_sets[j]

                if not set1 and not set2:
                    continue

                intersection = len(set1 & set2)
                union = len(set1 | set2)

                if union > 0:
                    similarities.append(intersection / union)

        overlap = float(np.mean(similarities)) if similarities else 1.0
        logger.debug(f"Key point overlap: {overlap:.3f}")

        return overlap

    def _confidence_to_float(self, confidence: ConfidenceLevel) -> float:
        """Convert confidence level to float."""
        return self.CONFIDENCE_MAP[confidence]

    def _generate_explanation(
        self,
        final_score: float,
        semantic_disagreement: float,
        confidence_variance: float,
        responses: Dict[str, ResearchResponse]
    ) -> str:
        """Generate human-readable explanation."""
        if final_score < 0.2:
            level = "Very high agreement"
            detail = "All models provide similar answers with consistent confidence levels."
        elif final_score < 0.4:
            level = "High agreement"
            detail = "Models largely agree, with minor variations in phrasing or confidence."
        elif final_score < 0.6:
            level = "Moderate disagreement"
            detail = "Models have overlapping claims but some notable differences."
        elif final_score < 0.8:
            level = "High disagreement"
            detail = "Models provide different answers or have significant confidence differences."
        else:
            level = "Very high disagreement"
            detail = "Models fundamentally disagree on the answer or have very low confidence."

        return f"{level} (score: {final_score:.2f}). {detail}"
