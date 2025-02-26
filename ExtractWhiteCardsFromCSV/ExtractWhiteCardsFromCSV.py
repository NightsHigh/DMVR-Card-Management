import csv
import os
import time
import re
import sqlite3
import requests

# File paths
red_conf = "OnlyRedCards.conf"
blue_conf = "OnlyBlueCards.conf"
all_cards_file = "AllCards.csv"
output_conf = "MissingCards.conf"

# Database files (adjust paths as needed)
IGNIS_DB_FILES = [
    "/home/soeren/.local/opt/edopro/app/expansions/cards.cdb",
    "/home/soeren/.local/opt/edopro/app/expansions/cards-unofficial.cdb",
]

def clean_card_name(card_name):
    """Remove unwanted designations from the card name."""
    unwanted = r"(Anime|Manga|VG|Video Game|Alternative Artwork)"
    return re.sub(r"\s*\(" + unwanted + r"\)", "", card_name, flags=re.IGNORECASE).strip()

def get_card_id_from_ygoprodeck(card_name):
    """Try fetching card ID from YGOPRODeck API (exact and fuzzy search)."""
    cleaned_name = clean_card_name(card_name)
    urls = [
        f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={requests.utils.quote(cleaned_name)}",
        f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={requests.utils.quote(cleaned_name)}"
    ]
    
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                    return str(data["data"][0].get("id"))
        except Exception as e:
            print(f"Error querying YGOPRODeck for '{card_name}': {e}")
        time.sleep(0.2)  # Respect API rate limit

    return None

def get_card_id_from_ignis(card_name):
    """Try fetching card ID from Project Ignis databases."""
    cleaned_name = clean_card_name(card_name)

    for db_file in IGNIS_DB_FILES:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM datas WHERE name = ?", (cleaned_name,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    print(f"Found '{card_name}' in {db_file} with ID: {row[0]}")
                    return str(row[0])
            except Exception as e:
                print(f"Error querying {db_file} for '{card_name}': {e}")

    return None

def get_card_id(card_name):
    """Try fetching card ID from YGOPRODeck API first, then from Ignis databases."""
    card_id = get_card_id_from_ygoprodeck(card_name) or get_card_id_from_ignis(card_name)
    if card_id is None:
        print(f"Card ID not found for: '{card_name}'")
    return card_id

def load_conf_file(filename):
    """Load card IDs from a .conf file."""
    card_ids = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split(" # ")
                if len(parts) > 1:
                    card_ids.add(parts[0].strip())
    return card_ids

def load_all_cards(filename):
    all_cards = []
    
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        
        # Skip unnecessary lines until the actual headers start
        for row in reader:
            if row and "Card ID" in row and "Card Name" in row:  # Ensure correct column detection
                headers = row
                break

        print("Detected Headers:", headers)  # Debugging: Check headers
        
        # Read actual card data
        for row in reader:
            if not row or len([r for r in row if r.strip()]) < 2:  # Skip empty or bad rows
                continue

            card_data = {headers[i].strip(): row[i].strip() for i in range(len(headers)) if i < len(row)}

            # Skip non-card rows
            if card_data.get("Card Name", "").strip() in ["Card Name", "Tier"]:
                continue

            all_cards.append(card_data)


            if len(all_cards) % 1000 == 0:  # Debugging: Print every 1000 rows
                print(f"Processed {len(all_cards)} cards...")
    print(f"✅ Successfully loaded {len(all_cards)} cards from CSV.")

    return all_cards



# Load existing red and blue card IDs
red_card_ids = load_conf_file(red_conf)
blue_card_ids = load_conf_file(blue_conf)

# Load all cards from CSV
all_cards = load_all_cards(all_cards_file)

# Process missing cards:
# Use the CSV "Card ID" if it exists and is numeric; otherwise, fetch using API/DB.
missing_cards = []
for card in all_cards:
    print(f"🔍 Looking up ID for: {card.get('Card Name', 'UNKNOWN')}")

    csv_card_id = card.get("Card ID", "").strip()
    if not csv_card_id or not csv_card_id.isdigit():
        csv_card_id = get_card_id(card.get("Card Name", ""))
        if csv_card_id:
            card["Card ID"] = csv_card_id
    if csv_card_id and csv_card_id not in red_card_ids and csv_card_id not in blue_card_ids:
        missing_cards.append(card)

# Deduplicate missing cards using a dictionary (unique by ID)
unique_missing_cards = {card["Card ID"]: card["Card Name"] for card in missing_cards if "Card Name" in card}

with open(output_conf, "w", encoding="utf-8") as file:
    for card_id, card_name in sorted(unique_missing_cards.items()):
        file.write(f"{card_id} 1 # {card_name},\n")

print(f"Processed {len(unique_missing_cards)} missing cards into '{output_conf}'")
