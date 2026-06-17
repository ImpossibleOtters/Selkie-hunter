import json

SEEN_FILE = "seen_items.json"

with open(SEEN_FILE, "r", encoding="utf-8") as f:
    seen_items = json.load(f)

test_link = "https://example.com/test-selkie-listing"

if test_link not in seen_items:
    seen_items.append(test_link)
    print("Added test item.")
else:
    print("Test item was already seen.")

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f, indent=2)

print("Seen items file updated successfully.")
