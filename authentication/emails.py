from django.core.mail import send_mail

def send_otp_email(to_email: str, code: str):
    subject = "Your verification code"
    body = f"Your One-Time Password (OTP) is: {code}. It will expire in 10 minutes."
    send_mail(subject, body, None, [to_email])
