"""
TypeFully Publisher Module (V2 API)

Publishes content to X/Twitter via Typefully API V2.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
import requests

logger = logging.getLogger(__name__)

# Singapore timezone (UTC+8)
SGT = timezone(timedelta(hours=8))


@dataclass
class PublishResult:
    """Result of a publishing attempt"""
    success: bool
    url: Optional[str] = None
    draft_id: Optional[str] = None
    scheduled_time: Optional[str] = None
    error_msg: Optional[str] = None


class TypefullyPublisher:
    """Publisher using Typefully API V2 for scheduled publishing"""

    def __init__(self, api_key: str, hours_delay: int = 6, publish_hour: int = 17, publish_now: bool = False):
        """
        Initialize Typefully publisher

        Args:
            api_key: Typefully API key (Bearer token)
            hours_delay: Hours to delay publishing (default: 6)
            publish_hour: Target hour in Singapore time to publish (default: 17 = 5 PM)
            publish_now: If True, publish immediately instead of scheduling
        """
        self.api_key = api_key
        self.hours_delay = hours_delay
        self.publish_hour = publish_hour
        self.publish_now = publish_now
        self.base_url = "https://api.typefully.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.social_set_id = None

        logger.info(f"Initialized TypefullyPublisher (V2 API)")
        if publish_now:
            logger.info(f"  Mode: INSTANT PUBLISH")
        else:
            logger.info(f"  Mode: Scheduled ({hours_delay} hours delay)")

    def _get_social_set_id(self) -> Optional[str]:
        """
        Get the first social set ID from the account.

        Returns:
            Social set ID or None if failed
        """
        if self.social_set_id:
            return self.social_set_id

        try:
            response = requests.get(
                f"{self.base_url}/social-sets",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                if results:
                    self.social_set_id = results[0].get('id')
                    logger.info(f"Found social set ID: {self.social_set_id}")
                    return self.social_set_id
                else:
                    logger.error("No social sets found in account")
                    return None
            else:
                logger.error(f"Failed to get social sets: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting social sets: {e}")
            return None

    def _calculate_publish_time(self) -> str:
        """
        Calculate the publish time based on hours_delay.

        Returns:
            ISO 8601 datetime string with Singapore timezone
        """
        now_sgt = datetime.now(SGT)
        publish_time = now_sgt + timedelta(hours=self.hours_delay)

        # Format as ISO 8601 with timezone
        # e.g., "2024-12-28T17:00:00+08:00"
        return publish_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

    def publish(self, content: str) -> PublishResult:
        """
        Create a scheduled draft in Typefully

        Args:
            content: Content to publish on X/Twitter

        Returns:
            PublishResult object
        """
        if not content or not content.strip():
            return PublishResult(
                success=False,
                error_msg="Content is empty"
            )

        # Get social set ID
        social_set_id = self._get_social_set_id()
        if not social_set_id:
            return PublishResult(
                success=False,
                error_msg="Failed to get social set ID"
            )

        try:
            # Calculate publish time
            if self.publish_now:
                publish_at = "now"
            else:
                publish_at = self._calculate_publish_time()

            # V2 API payload format
            # - enabled: true to activate platform
            # - posts: array of post objects with text field
            payload = {
                "platforms": {
                    "x": {
                        "enabled": True,
                        "posts": [
                            {"text": content}
                        ]
                    }
                },
                "publish_at": publish_at
            }

            response = requests.post(
                f"{self.base_url}/social-sets/{social_set_id}/drafts",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code in (200, 201):
                data = response.json()
                draft_id = data.get('id', 'unknown')
                draft_url = f"https://typefully.com/drafts/{draft_id}"

                logger.info(f"Created Typefully draft: {draft_url}")
                logger.info(f"Scheduled to publish at: {publish_at}")

                return PublishResult(
                    success=True,
                    url=draft_url,
                    draft_id=str(draft_id),
                    scheduled_time=publish_at
                )
            else:
                error_msg = f"Typefully API error: {response.status_code}"

                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = f"Typefully error: {error_data['error']}"
                    elif 'message' in error_data:
                        error_msg = f"Typefully error: {error_data['message']}"
                    elif 'detail' in error_data:
                        error_msg = f"Typefully error: {error_data['detail']}"
                except:
                    error_msg += f" - {response.text}"

                logger.error(error_msg)
                return PublishResult(success=False, error_msg=error_msg)

        except requests.exceptions.Timeout:
            return PublishResult(success=False, error_msg="Typefully API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Typefully request failed: {e}")
            return PublishResult(success=False, error_msg=f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return PublishResult(success=False, error_msg=f"Unexpected error: {str(e)}")
