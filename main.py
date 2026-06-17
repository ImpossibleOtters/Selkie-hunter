import os
import smtplib
import requests
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from urllib.parse import quote_plus

SEARCH_TERMS = [
    "Selkie Scottish Plaid Astronomer Gown",
    "Selkie Scotland Plaid Astronomer Gown",
    "Scottish Plaid Astronomer",
    "Scotland Plaid Astronomer",
    "Selkie Astronomer Plaid",
    "Selkie Plaid Astronomer",
    "Selkie tartan dress",
]

SEEN_FILE = "seen_items.txt"


def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for item in sorted(seen):
            f.write(item + "\n")


def is_likely_match(title):
    t = title.lower()
    return (
        "selkie" in t
        and (
            ("astronomer" in t and "plaid" in t)
            or ("astronomer" in t and "scotland" in t)
            or ("astronomer" in t and "scottish" in t)
            or ("tartan" in t and "selkie" in t)
        )
    )


def search_ebay():
    results = []

    for term in SEARCH_TERMS:
        url = (
            "https://www.ebay.com/sch/i.html?"
            f"_nkw={quote_plus(term)}"
            "&_rss=1"
        )

        print(f"Searching eBay: {term}")

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)

        for item in root.findall(".//item"):
            title = item.findtext("title", default="")
            link = item.findtext("link", default="")

            if title and link and is_likely_match(title):
                results.append({
                    "source": "eBay",
                    "title": title,
                    "link": link,
                })

    return results


def send_email(new_items):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    msg = EmailMessage()
    msg["Subject"] = f"🎉 Selkie Hunter found {len(new_items)} new listing(s)!"
    msg["From"] = sender
    msg["To"] = recipient

    body = "New possible Selkie Scottish Plaid Astronomer Gown listing(s):\n\n"

    for item in new_items:
        body += f"Source: {item['source']}\n"
        body += f"Title: {item['title']}\n"
        body += f"Link: {item['link']}\n\n"

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


def main():
    print("🔎 Selkie Hunter running")

    seen = load_seen()
    listings = search_ebay()

    print(f"Found {len(listings)} possible matching listing(s).")

    new_items = []
    for item in listings:
        item_id = item["link"]
        if item_id not in seen:
            new_items.append(item)
            seen.add(item_id)

    if new_items:
        print(f"Sending email for {len(new_items)} new listing(s).")
        send_email(new_items)
        save_seen(seen)
    else:
        print("No new listings found.")


if __name__ == "__main__":
    main()
