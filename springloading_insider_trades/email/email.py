import logging
import smtplib
import ssl
from typing import List

from settings import EMAIL_PASSWORD, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def _send_email(date_string: str, msg_body: str):
    port = 465  # For SSL
    password = EMAIL_PASSWORD

    # Create a secure SSL context
    context = ssl.create_default_context()

    sender_email = "connorv.dev@gmail.com"
    receiver_emails = ["connor.vanooyen@gmail.com"]

    # Message
    message = f'To: {",".join(receiver_emails)}\nSubject: Insider Trades Errors for {date_string}\n\n{msg_body}'

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("connorv.dev@gmail.com", password)
        server.sendmail(sender_email, receiver_emails, message)


def send_error_urls_email(date_string: str, error_urls: List[str]):
    msg_str: str = """"""

    for url in error_urls:
        msg_str += f"{url}\n\n"
    try:
        _send_email(date_string, msg_str)
    except Exception as e:
        logger.error(f"Failed to send email for errors -> {e}")
        return False

    return True
