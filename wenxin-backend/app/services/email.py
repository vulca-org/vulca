"""
Email service for sending transactional emails.

Supports:
- Async SMTP (SendGrid, SES, Mailgun, any SMTP provider)
- HTML and plain text templates
- Confirmation emails for leads
"""
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    import aiosmtplib
    HAS_AIOSMTPLIB = True
except ImportError:
    HAS_AIOSMTPLIB = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails via SMTP."""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS
        self.enabled = settings.ENABLE_EMAIL_CONFIRMATION

    def is_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return bool(self.host and self.user and self.password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.

        Returns True if sent successfully, False otherwise.
        Failures are logged but do not raise exceptions.
        """
        if not HAS_AIOSMTPLIB:
            logger.warning("aiosmtplib not installed, email sending disabled")
            return False

        if not self.enabled:
            logger.debug("Email sending is disabled")
            return False

        if not self.is_configured():
            logger.warning("SMTP not configured - skipping email send")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add plain text fallback
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            # Add HTML content
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send via SMTP
            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                start_tls=self.use_tls
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            if HAS_AIOSMTPLIB and isinstance(e, aiosmtplib.SMTPAuthenticationError):
                logger.error(f"SMTP authentication failed: {e}")
                return False
            if HAS_AIOSMTPLIB and isinstance(e, aiosmtplib.SMTPException):
                logger.error(f"SMTP error: {e}")
                return False
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_lead_confirmation(
        self,
        to_email: str,
        name: str,
        use_case: str,
        lead_id: str
    ) -> bool:
        """
        Send confirmation email to a new lead.

        Args:
            to_email: Lead's email address
            name: Lead's name
            use_case: Selected use case
            lead_id: Lead ID for reference
        """
        # Format use case for display
        use_case_display = {
            "ai_labs": "AI Labs - Pre-release cultural audits",
            "research": "Research - Academic benchmarking",
            "museums": "Museums - Cultural AI validation",
            "enterprise": "Enterprise - Custom evaluation",
            "other": "Custom evaluation"
        }.get(use_case, use_case)

        subject = "Thank you for your interest in VULCA"

        html_content = self._get_confirmation_html(
            name=name,
            use_case_display=use_case_display,
            lead_id=lead_id
        )

        text_content = self._get_confirmation_text(
            name=name,
            use_case_display=use_case_display,
            lead_id=lead_id
        )

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    def _get_confirmation_html(
        self,
        name: str,
        use_case_display: str,
        lead_id: str
    ) -> str:
        """Generate HTML email content for lead confirmation."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank you for your interest in VULCA</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1d1d1f;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f7;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo h1 {{
            color: #007AFF;
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        h2 {{
            color: #1d1d1f;
            font-size: 22px;
            margin-bottom: 20px;
        }}
        p {{
            color: #424245;
            margin-bottom: 16px;
        }}
        .highlight {{
            background: #f0f7ff;
            border-left: 4px solid #007AFF;
            padding: 16px 20px;
            margin: 24px 0;
            border-radius: 0 8px 8px 0;
        }}
        .highlight p {{
            margin: 0;
        }}
        .cta {{
            text-align: center;
            margin: 32px 0;
        }}
        .cta a {{
            display: inline-block;
            background: #007AFF;
            color: white;
            padding: 14px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            font-size: 16px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e5e5e7;
        }}
        .footer p {{
            color: #86868b;
            font-size: 14px;
            margin: 8px 0;
        }}
        .footer a {{
            color: #007AFF;
            text-decoration: none;
        }}
        .ref {{
            font-size: 12px;
            color: #86868b;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>VULCA</h1>
        </div>

        <h2>Thank you, {name}!</h2>

        <p>We've received your demo request and we're excited to show you how VULCA can help with your evaluation needs.</p>

        <div class="highlight">
            <p><strong>Your interest:</strong> {use_case_display}</p>
        </div>

        <p>A member of our team will reach out to you within 24 hours to schedule a personalized demo session.</p>

        <p>In the meantime, feel free to explore:</p>

        <div class="cta">
            <a href="https://vulcaart.art/vulca">Try the Public Demo</a>
        </div>

        <p>Or learn more about our methodology at <a href="https://vulcaart.art/methodology" style="color: #007AFF;">vulcaart.art/methodology</a></p>

        <div class="footer">
            <p>Have questions? Reply to this email or contact us at <a href="mailto:demo@vulcaart.art">demo@vulcaart.art</a></p>
            <p class="ref">Reference: {lead_id[:8]}</p>
            <p>VULCA - AI-Native Creation Organism</p>
        </div>
    </div>
</body>
</html>
"""

    def _get_confirmation_text(
        self,
        name: str,
        use_case_display: str,
        lead_id: str
    ) -> str:
        """Generate plain text email content for lead confirmation."""
        return f"""
Thank you, {name}!

We've received your demo request and we're excited to show you how VULCA can help with your evaluation needs.

Your interest: {use_case_display}

A member of our team will reach out to you within 24 hours to schedule a personalized demo session.

In the meantime, feel free to explore:
- Try the Public Demo: https://vulcaart.art/vulca
- Learn about our Methodology: https://vulcaart.art/methodology

Have questions? Reply to this email or contact us at demo@vulcaart.art

Reference: {lead_id[:8]}

---
VULCA - AI-Native Creation Organism
https://vulcaart.art
"""


# Singleton instance
email_service = EmailService()
