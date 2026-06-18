import json
import os
import smtplib
import requests
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from urllib.parse import quote_plus

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

item = config["item"]
sites = config["sites"]

sender = os.environ["EMAIL_SENDER"].strip()
password = os.environ["EMAIL_PASSWORD"].strip().replace(" ", "")
recipient = os.environ["EMAIL_RECIPIENT"].strip()

def score_match(title, link):
    text = f"{title} {link}".lower()

    if not all(word.lower() in text for word in item["must_include"]):
        return 0, []

    score = 0
    reasons = []

    for word in item["high_value_words"]:
        if word.lower() in text:
            score += 1
            reasons.append(word)

    if "astronomer" in text and ("plaid" in text or "tartan" in text or "scotland" in text or "scottish" in text):
        score += 5
        reasons.append("strong Astronomer + plaid/tartan match")

    return score, reasons

def send_email(title, link, source, score, reasons):
    msg = EmailMessage()
    msg["Subject"] = f"🚨 Selkie Hunter possible match: {score}/10"
    msg["From"] = sender
    msg["To"] = recipient

    msg.set_content(f"""Possible match found!

Item:
{item["name"]}

Source:
{source}

Title:
{title}

Score:
{score}

Why:
{", ".join(reasons)}

Link:
{link}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

print("🔎 Selkie Hunter searching...")

matches = []

for site in sites:
    for term in item["search_terms"]:
        query = f"site:{site} {term}"
        url = f"https://www.bing.com/search?q={quote_plus(query)}&format=rss"

        print(f"Searching: {query}")

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
            r.raise_for_status()
            root = ET.fromstring(r.content)

            for result in root.findall(".//item"):
                title = result.findtext("title", default="").strip()
                link = result.findtext("link", default="").strip()

                score, reasons = score_match(title, link)

                if score >= 5:
                    matches.append((title, link, site, score, reasons))

        except Exception as e:
            print(f"Search failed for {site}: {e}")

unique = {}
for title, link, site, score, reasons in matches:
    unique[link] = (title, link, site, score, reasons)

print(f"Found {len(unique)} possible match(es).")

SEEN_FILE = "seen_items.json"

try:
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_items = json.load(f)
except FileNotFoundError:
    seen_items = []

new_matches = []

for link, match in unique.items():
    if link not in seen_items:
        new_matches.append(match)
        seen_items.append(link)

if not new_matches:
    msg = EmailMessage()
    msg["Subject"] = "Selkie Hunter ran: no new matches"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("Selkie Hunter ran successfully but found no new listings.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
else:
    for title, link, site, score, reasons in sorted(new_matches, key=lambda x: x[3], reverse=True):
        send_email(title, link, site, score, reasons)
        print(f"Email sent for: {title}")

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f, indent=2)

print("Done.")
