import os
import smtplib
from email.message import EmailMessage

print("🔎 Selkie Hunter running")

sender = os.environ["EMAIL_SENDER"].strip()
password = os.environ["EMAIL_PASSWORD"].strip().replace(" ", "")
recipient = os.environ["EMAIL_RECIPIENT"].strip()

msg = EmailMessage()
msg["Subject"] = "Selkie Hunter test: ready for the real search"
msg["From"] = sender
msg["To"] = recipient
msg.set_content(
    "Selkie Hunter is still working after the requirements update. Next step: add the search code."
)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(sender, password)
    smtp.send_message(msg)

print("Email sent successfully.")
