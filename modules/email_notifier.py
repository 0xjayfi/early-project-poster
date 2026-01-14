"""
Email Notification Module

Sends email notifications using Gmail SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications via Gmail SMTP"""

    def __init__(self, gmail_address: str, gmail_app_password: str):
        """
        Initialize the email notifier.

        Args:
            gmail_address: Gmail address to send from (also used as recipient)
            gmail_app_password: Gmail app password (not regular password)
        """
        self.gmail_address = gmail_address
        self.gmail_app_password = gmail_app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_credential_expiry_notification(self, error_message: str) -> bool:
        """
        Send notification that Web3 Alerts credentials have expired.

        Args:
            error_message: The error message from credential validation

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "[Web3 Alerts Bot] Credentials Expired - Action Required"

        body = f"""Hi,

Your Web3 Alerts Twitter Bot was unable to run because the credentials have expired.

Error: {error_message}

To fix this:
1. Log in to https://web3alerts.app in your browser
2. Export your session cookies using a browser extension (e.g., "Cookie-Editor")
3. Save the cookies to credentials/cookies.json
4. If using GitHub Actions, update the COOKIES_JSON secret with the new cookie data

The bot will not post until this is resolved.

---
This is an automated message from Web3 Alerts Twitter Bot.
"""

        return self._send_email(subject, body)

    def _send_email(self, subject: str, body: str) -> bool:
        """
        Send an email via Gmail SMTP.

        Args:
            subject: Email subject
            body: Email body text

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.gmail_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                server.send_message(msg)

            logger.info(f"Email notification sent to {self.gmail_address}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Gmail authentication failed. Check email/app password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
