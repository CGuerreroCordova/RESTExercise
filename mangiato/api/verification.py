"""
Provide some functions to token generation, verification and to send emails
"""
import smtplib
from itsdangerous import URLSafeTimedSerializer
from email.message import EmailMessage
from mangiato.globals import APP


def generate_confirmation_token(email):
    """
    Generate a token of confirmation for account created and for invitations
    using secret keys
    :param email: email to generate token confirmation
    :type: str
    :return: token confirmation
    :type: str
    """
    serializer = URLSafeTimedSerializer(APP.config['SECRET_KEY'])
    return serializer.dumps(email, salt=APP.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    """
    Verify if a token is a valid token
    :param token: token to verify
    :type: str
    :param expiration: duration of token
    :type: int
    :return: email if is a valid token, false otherwise
    :type: str | boolean
    """
    serializer = URLSafeTimedSerializer(APP.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=APP.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(email_to, subject, template):
    """
    Send emails
    :param email_to: recipient
    :type: str
    :param subject: email subject
    :type: str
    :param template: email content
    :type: str
    :return: none
    :type: void
    """
    username = ""
    password = ""
    smtp_server = "smtp.gmail.com:587"
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email_to
    msg.add_alternative(template, subtype='html')
    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()
