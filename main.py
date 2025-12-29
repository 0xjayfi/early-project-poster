"""
Web3 Alerts to Twitter Bot

Fetches latest projects from Web3 Alerts and posts to Twitter via Typefully.
Uploads scheduled to post 6 hours later (Upload 11 AM SGT -> Publish 5 PM SGT).

Usage:
    python main.py          # Scheduled mode (publish in 6 hours)
    python main.py --now    # Instant mode (publish immediately)
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import List, Dict

import config
from modules.web3alerts_scraper import Web3AlertsScraper
from modules.typefully_publisher import TypefullyPublisher
from modules.gemini_summarizer import GeminiSummarizer

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_tweet(projects: List[Dict]) -> str:
    """
    Format projects into a single tweet.

    Args:
        projects: List of project dictionaries (with 'summary' field from Gemini)

    Returns:
        Formatted tweet string
    """
    today = datetime.now().strftime("%b %d")
    lines = [f"Early web3 projects ({today})"]

    for i, project in enumerate(projects, 1):
        name = project.get('project_name', 'Unknown')
        handle = project.get('handle', '')
        summary = project.get('summary', '')

        # Format: 1 project name (@handle): [summarized description]
        if handle:
            line = f"{i} {name} (@{handle})"
        else:
            line = f"{i} {name}"

        if summary:
            line += f": {summary}"

        lines.append(line)

    # Join with blank lines between projects for readability
    return "\n\n".join(lines)


def run_bot(publish_now: bool = False):
    """
    Main bot execution function.

    Args:
        publish_now: If True, publish immediately. If False, schedule for later.
    """
    logger.info("Starting Web3 Alerts Twitter Bot")

    if publish_now:
        logger.info("Mode: INSTANT PUBLISH")
        print("\n⚡ Running in INSTANT mode - will publish immediately!")
    else:
        logger.info(f"Mode: SCHEDULED (publish in {config.TYPEFULLY_HOURS_DELAY} hours)")
        print(f"\n📅 Running in SCHEDULED mode - will publish in {config.TYPEFULLY_HOURS_DELAY} hours")

    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)

    try:
        # Initialize scraper
        scraper = Web3AlertsScraper(config.COOKIES_PATH)

        # Fetch latest projects
        logger.info(f"Fetching {config.PROJECTS_COUNT} latest projects...")
        projects = scraper.get_latest_projects(count=config.PROJECTS_COUNT)

        if not projects:
            logger.warning("No projects found")
            return

        logger.info(f"Found {len(projects)} projects")

        # Summarize descriptions using Gemini
        logger.info("Summarizing project descriptions with Gemini...")
        summarizer = GeminiSummarizer(
            api_key=config.GEMINI_API_KEY,
            model=config.GEMINI_MODEL
        )
        projects = summarizer.summarize_projects(
            projects,
            max_words=config.SUMMARY_MAX_WORDS
        )

        # Format tweet
        tweet_content = format_tweet(projects)

        logger.info(f"Tweet content ({len(tweet_content)} chars):\n{tweet_content}")

        # Initialize publisher
        publisher = TypefullyPublisher(
            api_key=config.TYPEFULLY_API_KEY,
            hours_delay=config.TYPEFULLY_HOURS_DELAY,
            publish_hour=config.PUBLISH_HOUR_SGT,
            publish_now=publish_now
        )

        # Publish
        result = publisher.publish(tweet_content)

        if result.success:
            logger.info(f"Successfully created draft: {result.url}")
            print(f"\n✅ Draft created: {result.url}")
            if publish_now:
                print("⚡ Publishing immediately!")
            else:
                print(f"📅 Scheduled to publish at: {result.scheduled_time} (SGT)")
        else:
            logger.error(f"Failed to publish: {result.error_msg}")
            print(f"\n❌ Failed: {result.error_msg}")
            sys.exit(1)

    except Exception as e:
        logger.exception(f"Bot execution failed: {e}")
        sys.exit(1)


def main():
    """Parse arguments and run the bot."""
    parser = argparse.ArgumentParser(
        description="Web3 Alerts Twitter Bot - Post latest projects to X via Typefully"
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Publish immediately instead of scheduling for later"
    )

    args = parser.parse_args()
    run_bot(publish_now=args.now)


if __name__ == "__main__":
    main()
