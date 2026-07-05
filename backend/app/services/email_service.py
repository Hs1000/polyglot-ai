"""
Email service.

Sends transactional emails via Resend (resend.com).
All sending is best-effort: if RESEND_API_KEY is not set or the call fails,
the error is logged and the caller is not affected.
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _resend_ready() -> bool:
    return bool(settings.RESEND_API_KEY)


def send_welcome_email(to_email: str, name: str) -> None:
    """Send a welcome email. Silently skipped if RESEND_API_KEY is not set."""
    if not _resend_ready():
        return

    try:
        import resend

        resend.api_key = settings.RESEND_API_KEY

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:#2563eb;padding:32px 40px;text-align:center;">
              <span style="font-size:28px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">
                Polyglot AI Studio
              </span>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;">
              <h1 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#0f172a;">
                Welcome, {name}! 🎉
              </h1>
              <p style="margin:0 0 20px;font-size:15px;color:#475569;line-height:1.6;">
                Your account is ready. Here's what you can do with Polyglot AI Studio:
              </p>

              <!-- Features -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:12px 16px;background:#f8fafc;border-radius:10px;">
                    <span style="font-size:18px;">📄</span>
                    <strong style="color:#0f172a;font-size:14px;margin-left:10px;">Document Intelligence</strong>
                    <p style="margin:4px 0 0 32px;font-size:13px;color:#64748b;">Upload PDFs, images &amp; docs — get instant AI summaries and translations.</p>
                  </td>
                </tr>
                <tr><td style="height:8px;"></td></tr>
                <tr>
                  <td style="padding:12px 16px;background:#f8fafc;border-radius:10px;">
                    <span style="font-size:18px;">🌐</span>
                    <strong style="color:#0f172a;font-size:14px;margin-left:10px;">Bidirectional Translator</strong>
                    <p style="margin:4px 0 0 32px;font-size:13px;color:#64748b;">Translate between English and 15+ languages in real time.</p>
                  </td>
                </tr>
                <tr><td style="height:8px;"></td></tr>
                <tr>
                  <td style="padding:12px 16px;background:#f8fafc;border-radius:10px;">
                    <span style="font-size:18px;">🗂️</span>
                    <strong style="color:#0f172a;font-size:14px;margin-left:10px;">Document History</strong>
                    <p style="margin:4px 0 0 32px;font-size:13px;color:#64748b;">All your past analyses saved and accessible any time.</p>
                  </td>
                </tr>
              </table>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:32px;">
                <tr>
                  <td align="center">
                    <a href="{settings.FRONTEND_URL}"
                       style="display:inline-block;background:#2563eb;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:14px 32px;border-radius:10px;">
                      Open Studio →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="border-top:1px solid #e2e8f0;padding:20px 40px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#94a3b8;">
                You're receiving this because you created an account at Polyglot AI Studio.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        resend.Emails.send({
            "from": f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Welcome to Polyglot AI Studio!",
            "html": html,
        })

        logger.info("Welcome email sent to %s", to_email)

    except Exception:
        logger.exception("Failed to send welcome email to %s", to_email)
