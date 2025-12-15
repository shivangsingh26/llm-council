"""
Output Manager
==============
Handles saving research outputs to structured JSON files.

Learning Points:
- File I/O in Python (reading/writing files)
- JSON serialization with Pydantic
- Directory management and path handling
- Filename generation with timestamps
- Error handling for file operations

Why save outputs?
- Review past research results
- Analyze model performance over time
- Build a research database
- Debug issues with specific queries
- Track token usage and costs
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from src.models.schemas import ResearchResponse, ResearchDomain, ComparisonResult


class OutputManager:
    """
    Manages saving and loading research outputs.

    Directory Structure:
        outputs/
        ├── sports/
        ├── finance/
        ├── shopping/
        └── healthcare/

    File Naming:
        {timestamp}_{sanitized_query}.json
        Example: 2024-12-14_12-30-45_what_are_best_smartphones.json

    Learning: Using pathlib.Path instead of os.path (modern Python!)
    """

    def __init__(self, base_dir: str = "outputs"):
        """
        Initialize the output manager.

        Args:
            base_dir: Base directory for all outputs (default: "outputs")

        Learning: Path() creates a Path object for easier file operations
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """
        Create output directories if they don't exist.

        Creates:
        - Base outputs directory
        - Subdirectory for each domain
        - Council comparisons directory with domain subdirectories

        Learning: mkdir(parents=True, exist_ok=True) means:
        - parents=True: Create parent directories if needed
        - exist_ok=True: Don't error if directory already exists
        """
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Create domain subdirectories
        for domain in ResearchDomain:
            domain_dir = self.base_dir / domain.value
            domain_dir.mkdir(parents=True, exist_ok=True)

        # Create council comparisons directory with domain subdirectories
        council_dir = self.base_dir / "council_comparisons"
        council_dir.mkdir(parents=True, exist_ok=True)
        for domain in ResearchDomain:
            council_domain_dir = council_dir / domain.value
            council_domain_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ Output directories ready at: {self.base_dir.absolute()}")

    def save_research(
        self,
        research: ResearchResponse,
        include_metadata: bool = True
    ) -> Path:
        """
        Save a research response to a JSON file.

        Args:
            research: The research response to save
            include_metadata: Include extra metadata in JSON (default: True)

        Returns:
            Path: Path to the saved file

        Raises:
            IOError: If file cannot be written

        Learning: Pydantic makes JSON serialization super easy!
        """

        # Generate filename from timestamp and query
        filename = self._generate_filename(research.query, research.timestamp)

        # Get domain-specific directory
        domain_dir = self.base_dir / research.domain.value

        # Full file path
        file_path = domain_dir / filename

        # Convert Pydantic model to dictionary
        # model_dump() is the new way (replaces dict() in Pydantic v2)
        data = research.model_dump()

        # Add extra metadata if requested
        if include_metadata:
            data['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'file_path': str(file_path),
                'domain_directory': research.domain.value
            }

        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            print(f"💾 Saved: {file_path.name}")
            return file_path

        except Exception as e:
            print(f"❌ Failed to save output: {e}")
            raise

    def save_comparison(
        self,
        comparison: ComparisonResult,
        include_metadata: bool = True
    ) -> Path:
        """
        Save a council comparison result to a JSON file.

        Args:
            comparison: The comparison result to save
            include_metadata: Include extra metadata in JSON (default: True)

        Returns:
            Path: Path to the saved file

        Raises:
            IOError: If file cannot be written

        Learning: Council comparisons are saved to council_comparisons/{domain}/
        """

        # Generate filename from timestamp and query
        filename = self._generate_filename(comparison.query, comparison.timestamp)

        # Get council domain-specific directory
        council_dir = self.base_dir / "council_comparisons" / comparison.domain.value

        # Full file path
        file_path = council_dir / filename

        # Convert Pydantic model to dictionary
        data = comparison.model_dump()

        # Add extra metadata if requested
        if include_metadata:
            data['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'file_path': str(file_path),
                'domain_directory': comparison.domain.value,
                'type': 'council_comparison'
            }

        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            print(f"🏛️  Saved council comparison: {file_path.name}")
            return file_path

        except Exception as e:
            print(f"❌ Failed to save comparison: {e}")
            raise

    def load_research(self, file_path: str) -> dict:
        """
        Load a research response from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            dict: The research data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON

        Learning: You could return a ResearchResponse object using
        ResearchResponse(**data), but dict is more flexible for analysis.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in file: {e}")
            raise

    def list_outputs(
        self,
        domain: Optional[ResearchDomain] = None,
        limit: Optional[int] = None
    ) -> List[Path]:
        """
        List saved research outputs.

        Args:
            domain: Filter by specific domain (None = all domains)
            limit: Maximum number of files to return (None = all)

        Returns:
            List[Path]: List of file paths, sorted by newest first

        Learning: Path.glob() finds files matching a pattern
        """
        if domain:
            # Search specific domain directory
            pattern = f"{domain.value}/*.json"
        else:
            # Search all domain directories
            pattern = "*/*.json"

        # Find all matching files
        files = list(self.base_dir.glob(pattern))

        # Sort by modification time (newest first)
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Apply limit if specified
        if limit:
            files = files[:limit]

        return files

    def get_statistics(self) -> dict:
        """
        Get statistics about saved outputs.

        Returns:
            dict: Statistics including counts per domain, total tokens, etc.

        Learning: This shows how to aggregate data from multiple JSON files
        """
        stats = {
            'total_outputs': 0,
            'by_domain': {},
            'total_tokens': 0,
            'models_used': set()
        }

        # Count outputs per domain
        for domain in ResearchDomain:
            domain_files = list((self.base_dir / domain.value).glob("*.json"))
            count = len(domain_files)
            stats['by_domain'][domain.value] = count
            stats['total_outputs'] += count

            # Analyze each file
            for file in domain_files:
                try:
                    data = self.load_research(file)
                    if data.get('tokens_used'):
                        stats['total_tokens'] += data['tokens_used']
                    if data.get('model_name'):
                        stats['models_used'].add(data['model_name'])
                except:
                    pass  # Skip files we can't read

        # Convert set to list for JSON serialization
        stats['models_used'] = list(stats['models_used'])

        return stats

    def _generate_filename(self, query: str, timestamp: datetime) -> str:
        """
        Generate a unique filename from query and timestamp.

        Args:
            query: The research query
            timestamp: When the research was conducted

        Returns:
            str: Sanitized filename

        Format: {timestamp}_{sanitized_query}.json
        Example: 2024-12-14_12-30-45_what_are_best_smartphones.json

        Learning: Sanitizing filenames is important to avoid OS issues!
        """
        # Format timestamp: YYYY-MM-DD_HH-MM-SS
        time_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

        # Sanitize query for filename
        # 1. Take first 50 chars
        # 2. Convert to lowercase
        # 3. Replace spaces with underscores
        # 4. Remove special characters
        query_clean = query[:50].lower()
        query_clean = query_clean.replace(' ', '_')
        # Keep only alphanumeric and underscores
        query_clean = ''.join(c for c in query_clean if c.isalnum() or c == '_')

        # Combine timestamp and query
        filename = f"{time_str}_{query_clean}.json"

        return filename

    def __repr__(self) -> str:
        """String representation of the output manager."""
        return f"OutputManager(base_dir='{self.base_dir}')"


# Example usage and testing
if __name__ == "__main__":
    """
    Test the OutputManager.

    Run: python -m src.utils.output_manager
    """

    print("OutputManager Test")
    print("=" * 60)

    # Create manager
    manager = OutputManager()

    # Show directory structure
    print(f"\nBase directory: {manager.base_dir.absolute()}")
    print("\nDomain directories:")
    for domain in ResearchDomain:
        domain_dir = manager.base_dir / domain.value
        print(f"  • {domain.value}: {domain_dir}")

    # Get statistics
    stats = manager.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total outputs: {stats['total_outputs']}")
    print(f"  By domain:")
    for domain, count in stats['by_domain'].items():
        print(f"    - {domain}: {count}")

    if stats['total_outputs'] > 0:
        print(f"\n  Total tokens used: {stats['total_tokens']}")
        print(f"  Models used: {', '.join(stats['models_used'])}")

        # List recent outputs
        print(f"\n📁 Recent outputs:")
        recent = manager.list_outputs(limit=5)
        for i, file in enumerate(recent, 1):
            print(f"  {i}. {file.name}")
    else:
        print("\n💡 No outputs saved yet. Run test_single_agent.py to generate some!")
