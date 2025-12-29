"""
Gemini AI Summarizer Module

Uses Google's Gemini API to summarize project descriptions.
"""

import logging
import time
from typing import List, Dict, Optional
from google import genai

logger = logging.getLogger(__name__)

# Rate limiting: 15 RPM for gemini-2.5-flash-lite = 4 seconds between requests
RATE_LIMIT_DELAY = 4.0


class GeminiSummarizer:
    """Summarizes project descriptions using Gemini AI"""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini summarizer.

        Args:
            api_key: Google Gemini API key
            model: Model to use (default: gemini-2.5-flash-lite for best rate limits)
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        logger.info(f"Initialized GeminiSummarizer with model: {model}")

    def summarize_description(self, description: str, max_words: int = 10) -> str:
        """
        Summarize a single project description.

        Args:
            description: Original project description
            max_words: Maximum words for summary

        Returns:
            Summarized description
        """
        if not description or len(description.strip()) < 20:
            return description.strip() if description else ""

        prompt = f"""Summarize this Web3 project description in {max_words} words or less.
Extract the key value proposition. Be concise. No quotes or explanations.

Description: {description}

Summary:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            summary = response.text.strip()
            # Remove any quotes if present
            summary = summary.strip('"\'')
            return summary
        except Exception as e:
            logger.warning(f"Summarization failed: {e}, using truncated original")
            # Fallback to truncation
            words = description.split()[:max_words]
            return " ".join(words) + "..." if len(description.split()) > max_words else description

    def summarize_projects(self, projects: List[Dict], max_words: int = 10) -> List[Dict]:
        """
        Summarize descriptions for a list of projects.

        Args:
            projects: List of project dictionaries
            max_words: Maximum words per summary

        Returns:
            Projects with summarized descriptions
        """
        logger.info(f"Summarizing {len(projects)} project descriptions...")

        prompt = self._build_batch_prompt(projects, max_words)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            summaries = self._parse_batch_response(response.text, len(projects))

            # Update projects with summaries
            for i, project in enumerate(projects):
                if i < len(summaries) and summaries[i]:
                    project['summary'] = summaries[i]
                else:
                    project['summary'] = self.summarize_description(
                        project.get('description', ''), max_words
                    )

            logger.info("Batch summarization completed")
            return projects

        except Exception as e:
            logger.warning(f"Batch summarization failed: {e}, falling back to individual")
            # Fallback to individual summarization with rate limiting
            for i, project in enumerate(projects):
                if i > 0:
                    time.sleep(RATE_LIMIT_DELAY)  # Respect rate limits
                project['summary'] = self.summarize_description(
                    project.get('description', ''), max_words
                )
            return projects

    def _build_batch_prompt(self, projects: List[Dict], max_words: int) -> str:
        """Build a batch prompt for summarizing multiple projects."""
        prompt = f"""Summarize each Web3 project description below in {max_words} words or less.
Extract the key value proposition for each. Be concise.
Return ONLY the summaries, one per line, numbered 1-{len(projects)}.

"""
        for i, project in enumerate(projects, 1):
            name = project.get('project_name', 'Unknown')
            desc = project.get('description', 'No description')
            prompt += f"{i}. {name}: {desc}\n"

        prompt += "\nSummaries (one per line, numbered):"
        return prompt

    def _parse_batch_response(self, response_text: str, expected_count: int) -> List[str]:
        """Parse batch response into individual summaries."""
        summaries = []
        lines = response_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove numbering like "1.", "1)", "1:"
            for prefix in [f"{i}." for i in range(1, expected_count + 1)]:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            for prefix in [f"{i})" for i in range(1, expected_count + 1)]:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            for prefix in [f"{i}:" for i in range(1, expected_count + 1)]:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break

            # Remove quotes
            line = line.strip('"\'')
            if line:
                summaries.append(line)

        return summaries
