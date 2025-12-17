"""
Dynamic prompt selector for LLM Council.

Selects optimal prompts based on:
1. Research domain (finance, sports, shopping, healthcare)
2. Query complexity (simple, moderate, complex)
3. Tool availability (web search, APIs, code execution)
"""

from typing import Dict, List, Optional
from src.models.schemas import ResearchDomain


class PromptSelector:
    """
    Intelligent prompt selection system.

    Provides domain-specific expertise and complexity-aware
    templates to maximize research quality.
    """

    # Domain-specific system prompts with specialized knowledge
    DOMAIN_PROMPTS = {
        ResearchDomain.FINANCE: """You are an expert financial analyst with deep knowledge of:
- Stock markets, trading, and investment strategies
- Company financials, earnings, and valuation metrics
- Economic indicators and market trends
- Financial regulations and compliance
- Risk assessment and portfolio management

Key principles:
✓ Always cite specific data sources (prices, volumes, dates)
✓ Include market context (trends, news, sentiment)
✓ Provide balanced analysis of risks and opportunities
✓ Use precise financial terminology
✓ Consider both fundamental and technical factors

⚠️ IMPORTANT DISCLAIMER:
This is informational research only, not financial advice.
Always consult a qualified financial advisor before making investment decisions.""",

        ResearchDomain.SPORTS: """You are a professional sports analyst with expertise in:
- Live scores, statistics, and standings across major leagues
- Player performance metrics and analytics
- Team strategies, coaching, and roster analysis
- Historical records and performance trends
- Injury reports and lineup changes

Key principles:
✓ Provide specific stats and numbers when available
✓ Note the date/time of data (sports change rapidly)
✓ Consider recent form and momentum
✓ Acknowledge uncertainty in predictions
✓ Cover multiple aspects (offense, defense, special teams, etc.)

Focus on factual analysis over speculation.""",

        ResearchDomain.SHOPPING: """You are a consumer product expert specializing in:
- Product comparisons and feature analysis
- Price-to-value assessment and deal identification
- Review aggregation and sentiment analysis
- Brand reputation and reliability
- Product specifications and compatibility

Key principles:
✓ Compare multiple options when possible
✓ Consider total cost of ownership (price + maintenance + longevity)
✓ Highlight key differentiators between products
✓ Note availability and shipping considerations
✓ Mention both pros and cons objectively

Help users make informed purchasing decisions.""",

        ResearchDomain.HEALTHCARE: """You are a medical research expert with knowledge of:
- Medications, treatments, and therapeutic approaches
- Medical conditions, symptoms, and diagnosis
- Clinical research and evidence-based medicine
- Healthcare best practices and guidelines
- Drug interactions and side effects

Key principles:
✓ Cite medical sources (FDA, NIH, peer-reviewed journals)
✓ Distinguish between FDA-approved and experimental treatments
✓ Note when medical consultation is essential
✓ Consider patient safety and well-being first
✓ Provide evidence-based information

⚠️ CRITICAL DISCLAIMER:
This is educational information only, not medical advice.
Always consult qualified healthcare professionals for medical decisions.
Never delay seeking professional medical care."""
    }

    # Query complexity templates
    COMPLEXITY_TEMPLATES = {
        "simple": """Provide a clear, concise answer in 2-3 sentences.
Focus on the most important facts without unnecessary detail.""",

        "moderate": """Provide a comprehensive answer structured as follows:

1. **Main Answer** (2-3 paragraphs)
   - Core information addressing the query
   - Key context and background

2. **Key Points** (3-5 bullet points)
   - Supporting details
   - Important considerations
   - Relevant data or statistics

3. **Additional Notes**
   - Caveats or limitations
   - Related information""",

        "complex": """Provide an in-depth analysis structured as follows:

1. **Executive Summary**
   - Brief overview (2-3 sentences)
   - Main conclusion or recommendation

2. **Detailed Analysis**
   - Comprehensive explanation (3-4 paragraphs)
   - Multiple perspectives or approaches
   - Supporting evidence and data

3. **Key Supporting Points** (5-7 bullet points)
   - Critical details
   - Statistical evidence
   - Expert opinions or research findings

4. **Considerations and Caveats**
   - Limitations of the analysis
   - Assumptions made
   - Areas of uncertainty

5. **Practical Recommendations**
   - Actionable insights
   - Next steps or further research needed"""
    }

    # Complexity indicators that suggest a complex query
    COMPLEX_INDICATORS = [
        'compare', 'analyze', 'evaluate', 'assess',
        'pros and cons', 'advantages and disadvantages',
        'why', 'how', 'explain', 'breakdown',
        'comprehensive', 'detailed', 'in-depth',
        'vs', 'versus', 'difference between',
        'best', 'optimal', 'recommend'
    ]

    # Simple query indicators
    SIMPLE_INDICATORS = [
        'what is', 'who is', 'when',
        'current', 'latest', 'today',
        'price of', 'score', 'result'
    ]

    def analyze_query_complexity(self, query: str) -> str:
        """
        Determine query complexity level.

        Args:
            query: Research query to analyze

        Returns:
            "simple", "moderate", or "complex"
        """
        query_lower = query.lower()
        word_count = len(query.split())

        # Check for simple indicators first
        if any(indicator in query_lower for indicator in self.SIMPLE_INDICATORS):
            if word_count < 10:
                return "simple"

        # Check for complex indicators
        if any(indicator in query_lower for indicator in self.COMPLEX_INDICATORS):
            return "complex"

        # Default based on length
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"

    def get_tools_instruction(self, available_tools: List[str]) -> str:
        """
        Generate instruction for tool usage.

        Args:
            available_tools: List of tool names available to the agent

        Returns:
            Formatted tool instruction string
        """
        if not available_tools:
            return ""

        tool_descriptions = {
            "web_search": "🔍 Web search for current, real-time information",
            "finance_api": "📊 Stock prices, market data, and financial news",
            "sports_api": "⚽ Live scores, stats, and sports news",
            "shopping_api": "🛍️ Product search, prices, and reviews",
            "healthcare_api": "🏥 Drug information and medical research",
            "calculator": "🧮 Precise mathematical calculations",
            "code_executor": "💻 Python code execution for complex computations"
        }

        tools_list = "\n".join([
            f"  • {tool_descriptions.get(tool, tool)}"
            for tool in available_tools
        ])

        return f"""
📋 **Tools Available:**
{tools_list}

Use these tools when they would improve accuracy, provide real-time data,
or enable precise calculations. Always cite tool results in your answer."""

    def get_prompt(
        self,
        query: str,
        domain: ResearchDomain,
        available_tools: Optional[List[str]] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate optimal prompt for the given query.

        Args:
            query: Research query
            domain: Research domain (finance, sports, etc.)
            available_tools: List of available tool names
            max_tokens: Token limit for response

        Returns:
            Dict with 'system' and 'user' prompts
        """
        # 1. Get domain-specific expertise
        domain_prompt = self.DOMAIN_PROMPTS.get(
            domain,
            "You are a helpful research assistant."
        )

        # 2. Analyze complexity
        complexity = self.analyze_query_complexity(query)
        complexity_template = self.COMPLEXITY_TEMPLATES[complexity]

        # 3. Add tool instructions if tools available
        tools_instruction = ""
        if available_tools:
            tools_instruction = self.get_tools_instruction(available_tools)

        # 4. Add length guidance if max_tokens specified
        length_guidance = ""
        if max_tokens:
            if max_tokens < 300:
                length_guidance = "\n⚠️ Keep response concise (under 200 words)."
            elif max_tokens < 600:
                length_guidance = "\n⚠️ Keep response moderate length (under 400 words)."

        # Build system prompt
        system_prompt = f"""{domain_prompt}

{tools_instruction}

**Response Format:**
{complexity_template}{length_guidance}"""

        # Build user prompt
        user_prompt = f"""Research Query: {query}

Domain: {domain.value}
Complexity Level: {complexity}

Please provide a well-researched answer following the response format guidelines."""

        return {
            "system": system_prompt.strip(),
            "user": user_prompt.strip(),
            "metadata": {
                "domain": domain.value,
                "complexity": complexity,
                "tools_available": available_tools or [],
                "max_tokens": max_tokens
            }
        }

    def get_synthesis_prompt(
        self,
        query: str,
        agent_responses: Dict[str, str],
        domain: ResearchDomain
    ) -> str:
        """
        Generate prompt for the master synthesizer (O1 model).

        Args:
            query: Original research query
            agent_responses: Dict of agent_name -> response
            domain: Research domain

        Returns:
            Synthesis prompt for O1 model
        """
        # Format agent responses
        responses_text = "\n\n".join([
            f"### {agent_name}\n{response}"
            for agent_name, response in agent_responses.items()
        ])

        return f"""# Research Synthesis Task

## Original Query
{query}

## Domain
{domain.value}

## Agent Responses
{responses_text}

## Your Task

As the master synthesizer, analyze all agent responses and provide:

1. **Consensus Analysis**
   - Identify points where agents genuinely agree (semantic agreement)
   - Explain WHY these represent consensus
   - Rank by importance

2. **Disagreement Analysis**
   - Identify meaningful disagreements (not superficial differences)
   - Explain the root cause of each disagreement
   - Assess which perspective is more credible (with reasoning)

3. **Synthesized Answer**
   - Provide a coherent, well-reasoned synthesis
   - Integrate insights from all agents
   - Resolve disagreements with clear reasoning
   - Add your own analysis where appropriate

4. **Confidence Assessment**
   - Overall confidence level (low/medium/high/very_high)
   - Reasoning for this confidence score
   - Key uncertainties or limitations

5. **Quality Indicators**
   - Are there factual claims that need verification?
   - Is the information current and up-to-date?
   - Are there any contradictions or inconsistencies?

Think deeply, reason carefully, and provide your best synthesis."""


# Convenience function for quick prompt generation
def get_research_prompt(
    query: str,
    domain: ResearchDomain,
    available_tools: Optional[List[str]] = None,
    max_tokens: Optional[int] = None
) -> Dict[str, str]:
    """
    Quick function to get research prompt.

    Args:
        query: Research query
        domain: Research domain
        available_tools: List of available tools
        max_tokens: Token limit

    Returns:
        Dict with system and user prompts
    """
    selector = PromptSelector()
    return selector.get_prompt(query, domain, available_tools, max_tokens)
