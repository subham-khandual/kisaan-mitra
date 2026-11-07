"""
Email Service using Gmail SMTP for OTP Verification & Farmer Notifications.
"""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_email = settings.SMTP_EMAIL
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_name = settings.SMTP_FROM_NAME

    def _send_sync(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Synchronous SMTP sending with SSL/TLS fallback."""
        if not self.smtp_email or not self.smtp_password:
            raise RuntimeError("SMTP credentials not configured in backend/.env")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.smtp_email}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # Try SSL first (Port 465)
        try:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=12) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
                return True
        except Exception as ssl_err:
            print(f"[!] SMTP SSL attempt failed ({ssl_err}), trying STARTTLS on port 587...")
            # Fallback to STARTTLS on port 587
            try:
                with smtplib.SMTP(self.smtp_host, 587, timeout=12) as server:
                    server.starttls()
                    server.login(self.smtp_email, self.smtp_password)
                    server.send_message(msg)
                    return True
            except Exception as tls_err:
                print(f"[ERROR] SMTP sending failed: {tls_err}")
                raise tls_err

    async def send_otp_email(self, to_email: str, otp: str, purpose: str = "Registration") -> bool:
        """
        Sends an attractive HTML OTP verification email to the user.
        Runs asynchronously via asyncio.to_thread so it doesn't block FastAPI.
        """
        subject = f"🌾 {otp} is your Kisaan Mitra verification code"
        
        text_content = f"""
Hello Farmer,

Your Kisaan Mitra verification code for {purpose} is: {otp}

This code is valid for 10 minutes. Please do not share this OTP with anyone.

Best regards,
Kisaan Mitra Team
        """.strip()

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 20px;
    }}
    .email-container {{
      max-width: 520px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
      border: 1px solid #e5e7eb;
    }}
    .header {{
      background: linear-gradient(135deg, #15803d 0%, #166534 100%);
      color: #ffffff;
      padding: 30px 20px;
      text-align: center;
    }}
    .header h1 {{
      margin: 8px 0 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 4px 0 0;
      font-size: 14px;
      opacity: 0.9;
    }}
    .content {{
      padding: 32px 28px;
      color: #374151;
      line-height: 1.6;
    }}
    .otp-card {{
      background: #f0fdf4;
      border: 2px dashed #22c55e;
      border-radius: 10px;
      padding: 24px;
      text-align: center;
      margin: 24px 0;
    }}
    .otp-label {{
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #15803d;
      font-weight: 600;
      margin-bottom: 8px;
    }}
    .otp-code {{
      font-size: 38px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #166534;
      font-family: 'Courier New', monospace;
      margin: 0;
    }}
    .badge-info {{
      display: inline-block;
      font-size: 12px;
      color: #6b7280;
      margin-top: 10px;
    }}
    .footer {{
      background: #f9fafb;
      padding: 20px;
      text-align: center;
      font-size: 12px;
      color: #9ca3af;
      border-top: 1px solid #f3f4f6;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div style="font-size: 40px;">🌾</div>
      <h1>Kisaan Mitra</h1>
      <p>Smart Assistant for Indian Farmers</p>
    </div>
    <div class="content">
      <p style="font-size: 16px; margin-top: 0;">Namaste,</p>
      <p>You requested a verification code for <strong>{purpose}</strong> on Kisaan Mitra.</p>
      
      <div class="otp-card">
        <div class="otp-label">Verification Code</div>
        <div class="otp-code">{otp}</div>
        <div class="badge-info">⏱️ Valid for 10 minutes</div>
      </div>

      <p style="font-size: 14px; color: #4b5563;">
        If you did not request this code, you can safely ignore this email. Someone may have entered your email address by mistake.
      </p>
    </div>
    <div class="footer">
      <p>© 2026 Kisaan Mitra. Empowering Farmers with AI & Real-time Agri Intelligence.</p>
    </div>
  </div>
</body>
</html>
        """.strip()

        return await asyncio.to_thread(
            self._send_sync,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )


email_service = EmailService()
