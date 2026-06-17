import json
import os
import smtplib
from email.message import EmailMessage

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

print("🔎 Selkie Hunter running")
print(f"Looking for: {config['dress_name']}")

sender = os.environ["EMAIL_SENDER"].strip()
password = os.environ["EMAIL_PASSWORD"].strip().replace(" ", "")
recipient = os.environ["EMAIL_RECIPIENT"].strip()

msg = EmailMessage()
msg["Subject"] = "Selkie Hunter config test"
msg["From"] = sender
msg["To"] = recipient

body = f"""Selkie Hunter loaded your config successfully.

Dress:
{config['dress_name']}

Sizes:
{', '.join(config['sizes'])}

Search terms:
{chr(10).join('- ' + term for term in config['search_terms'])}
"""

msg.set_content(body)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(sender, password)
    smtp.send_message(msg)

print("Config email sent successfully.")
