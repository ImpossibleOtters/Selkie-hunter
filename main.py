import os
import smtplib
from email.message import EmailMessage

sender = os.environ["EMAIL_SENDER"]
password = os.environ["EMAIL_PASSWORD"]
recipient = os.environ["EMAIL_RECIPIENT"]

msg = EmailMessage()
msg["Subject"] = "🎉 Selkie Hunter is Alive!"
msg["From"] = sender
msg["To"] = recipient

msg.set_content(
    """
Your Selkie Hunter is running successfully!

Soon I'll be searching:

- eBay
- Depop
- Mercari
- Poshmark
- Vinted

for the Selkie Scottish Plaid Astronomer Gown in sizes S, M, and L.
"""
)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(sender, password)
    smtp.send_message(msg)

print("Email sent successfully.")
