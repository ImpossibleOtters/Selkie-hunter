import json
import os
import smtplib
import requests
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from urllib.parse import quote_plus

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SITES = ["ebay.com", "poshmark.com", "mercari.com", "depop.com", "vinted.com"]

sender = os.environ["EMAIL_SENDER"].strip()
password = os.environ["EMAIL_PASSWORD"].strip().replace(" ", "")
recipient = os.environ["EMAIL_RECIPIENT"].strip()

def send_email(title, link, source):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Possible Selkie Astronomer Gown listing found!"
    msg["From"] = sender
    msg["To"] = recipient

    msg.set_content(f"""Possible match found!

Dress:
{config["dress_name"]}

Source:
{source}

Title:
{title}

Link:
{link}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

def is_match(title, link):
    text = f"{title} {link}".lower()
    return (
        "selkie" in text
        and (
            "astronomer" in text
            or "astronomers" in text
            or "scottish plaid" in text
            or "scotland plaid" in text
            or "tartan" in text
        )
    )

print("🔎 Selkie Hunter searching...")

matches = []

for site in SITES:
    for term in config["search_terms"]:
        query = f"site:{site} {term}"
        url = f"https://www.bing.com/search?q={quote_plus(query)}&format=rss"

        print(f"Searching: {query}")

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
            r.raise_for_status()

            root = ET.fromstring(r.content)

            for item in root.findall(".//item"):
                title = item.findtext("title", default="").strip()
                link = item.findtext("link", default="").strip()

                if title and link and is_match(title, link):
                    matches.append((title, link, site))

        except Exception as e:
            print(f"Search failed for {site}: {e}")

unique = {}
for title, link, site in matches:
    unique[link] = (title, link, site)
print(f"Found {len(unique)} possible match(es).")

SEEN_FILE = "seen_items.json"

try:
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_items = json.load(f)
except FileNotFoundError:
        seen_items = []

new_matches = []

for link, item in unique.items():
    if link not in seen_items:
        new_matches.append(item)
        seen_items.append(link)

if not new_matches:
    msg = EmailMessage()
    msg["Subject"] = "Selkie Hunter ran: no new matches"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(
        "Selkie Hunter ran successfully but found no new listings."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

else:
    for title, link, site in new_matches:
        send_email(title, link, site)
        print(f"Email sent for: {title}")

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f, indent=2)

print("Done.")
