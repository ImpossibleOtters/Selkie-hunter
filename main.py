import json

SEEN_FILE = "seen_items.json"

# Load existing seen items
with open(SEEN_FILE, "r", encoding="utf-8") as f:
    seen = json.load(f)

print(f"Already tracking {len(seen)} items.")

# Fake listing for testing
listing = {
    "title": "Test Selkie Listing",
    "url": "https://example.com/test"
}

if listing["url"] in seen:
    print("Already seen.")
else:
    print("New listing found!")
    seen.append(listing["url"])

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2)

    print("Saved.")
