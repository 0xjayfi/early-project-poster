"""Configuration management for Web3 Alerts Twitter Bot."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
COOKIES_PATH = os.getenv('COOKIES_PATH', str(BASE_DIR / 'credentials' / 'cookies.json'))

# Typefully Configuration
TYPEFULLY_API_KEY: Optional[str] = os.getenv('TYPEFULLY_API_KEY')

# Scheduling Configuration
# Hours to delay before publishing (default: 6 hours)
# Upload at 11 AM SGT -> Publish at 5 PM SGT
TYPEFULLY_HOURS_DELAY: int = int(os.getenv('TYPEFULLY_HOURS_DELAY', '6'))

# Target publish hour in Singapore time (24-hour format, default: 17 = 5 PM)
PUBLISH_HOUR_SGT: int = int(os.getenv('PUBLISH_HOUR_SGT', '17'))

# Bot Configuration
PROJECTS_COUNT: int = int(os.getenv('PROJECTS_COUNT', '10'))
MAX_DESCRIPTION_LENGTH: int = int(os.getenv('MAX_DESCRIPTION_LENGTH', '80'))
SUMMARY_MAX_WORDS: int = int(os.getenv('SUMMARY_MAX_WORDS', '10'))

# Gemini AI Configuration
GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')

# Logging Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

# Upload schedule time in Singapore time (for cron-like scheduling)
# Default: 11:00 (11 AM SGT, 6 hours before 5 PM publish time)
UPLOAD_TIME_SGT: str = os.getenv('UPLOAD_TIME_SGT', '11:00')


def validate_config() -> bool:
    """Validate that all required configuration is present."""
    errors = []

    if not TYPEFULLY_API_KEY or TYPEFULLY_API_KEY.startswith('your_'):
        errors.append("TYPEFULLY_API_KEY is missing or invalid")

    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith('your_'):
        errors.append("GEMINI_API_KEY is missing or invalid")

    if not Path(COOKIES_PATH).exists():
        errors.append(f"Cookies file not found: {COOKIES_PATH}")

    if errors:
        for error in errors:
            print(f"Config Error: {error}")
        return False

    return True
