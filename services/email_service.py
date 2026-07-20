import smtplib
from email.message import EmailMessage
from typing import Any


def send_appointment_confirmation(
    appointment: dict[str, Any],
    appointment_id: int,
    smtp_host: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    business_name: str
) -> tuple[bool, str]:
    """
    Send an appointment confirmation email.

    Returns:
        (True, success message) when the email is sent.
        (False, error message) when sending fails.
    """
    recipient_email = appointment.get("email_address", "").strip()

    if not recipient_email:
        return False, "The customer email address is missing."

    message = EmailMessage()
    message["Subject"] = (
        f"Appointment Confirmation - Booking #{appointment_id}"
    )
    message["From"] = sender_email
    message["To"] = recipient_email

    email_body = f"""
Hello {appointment["full_name"]},

Your appointment with {business_name} has been confirmed.

Booking ID: {appointment_id}
Date: {appointment["appointment_date"]}
Time: {appointment["appointment_time"]}
Appointment Type: {appointment["appointment_type"]}
Reason: {appointment["reason"]}
Status: Confirmed

Please keep your Booking ID for reference.

Regards,
{business_name}
""".strip()

    message.set_content(email_body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        return True, "Confirmation email sent successfully."

    except smtplib.SMTPAuthenticationError:
        return False, (
            "Email authentication failed. "
            "Please check the sender email and app password."
        )

    except smtplib.SMTPException as error:
        return False, f"Email service error: {error}"

    except OSError as error:
        return False, f"Network error while sending email: {error}"