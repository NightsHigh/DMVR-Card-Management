import re
import sqlite3
import requests
import time
import os
# File paths
banlist_extra_file = "BanlistExtra.txt"
conf_files = {
    "B": "OnlyBlueCards.conf",
    "C": "OnlyRedCards.conf",
    "D": "OnlyWhiteCards.conf"
}

# Database files
IGNIS_DB_FILES = [
    "/home/soeren/.local/opt/edopro/app/expansions/cards.cdb",
    "/home/soeren/.local/opt/edopro/app/expansions/cards-unofficial.cdb",
]

def clean_card_name(card_name):
    """Removes unnecessary tags from card names."""
    unwanted = r"(Anime|Manga|VG|Video Game|Alternative Artwork)"
    return re.sub(r"\s*\(" + unwanted + r"\)", "", card_name, flags=re.IGNORECASE).strip()

def get_card_id_from_ygoprodeck(card_name):
    """Fetches card ID from YGOPRODeck API."""
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
    """Fetches card ID from Project Ignis databases."""
    cleaned_name = clean_card_name(card_name)
    for db_file in IGNIS_DB_FILES:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(datas)")
                columns = [row[1] for row in cursor.fetchall()]
                name_column = "name" if "name" in columns else "text"  # Adjust column name if necessary
                cursor.execute(f"SELECT id FROM datas WHERE {name_column} = ?", (cleaned_name,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    return str(row[0])
            except Exception as e:
                print(f"Error querying {db_file} for '{card_name}': {e}")
    return None

def get_card_id(card_name):
    """Fetches card ID from API first, then local database."""
    return get_card_id_from_ygoprodeck(card_name) or get_card_id_from_ignis(card_name)

def parse_extra_banlist(file_path):
    """Parses the extra deck banlist and categorizes cards into tiers B, C, and D."""
    banlist = {"B": [], "C": [], "D": []}
    current_tier = None
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if "Tier B Cards" in line:
                current_tier = "B"
            elif "Tier C Cards" in line:
                current_tier = "C"
            elif "Tier D Cards" in line:
                current_tier = "D"
            elif current_tier and line:
                banlist[current_tier].append(line)
    return banlist

def update_conf_file(conf_file, new_cards):
    """Adds new extra deck monsters to the specified .conf file with their IDs, avoiding duplicates."""
    existing_cards = set()
    updated_lines = []
    try:
        with open(conf_file, "r", encoding="utf-8") as file:
            for line in file:
                match = re.match(r"(\d+) \d # (.+),", line)
                if match:
                    card_id, card_name = match.groups()
                    existing_cards.add(card_name.strip().lower())  # Store in lowercase to avoid case mismatches
                updated_lines.append(line.strip())
    except FileNotFoundError:
        print(f"{conf_file} not found. Creating a new one.")
    
    for card_name in new_cards:
        if card_name.lower() not in existing_cards:
            card_id = get_card_id(card_name) or "00000000"  # Default ID if not found
            updated_lines.append(f"{card_id} 1 # {card_name},")
    
    with open(conf_file, "w", encoding="utf-8") as file:
        file.write("\n".join(updated_lines) + "\n")
    print(f"Updated {conf_file} with {len(new_cards)} new extra deck monsters.")

banlist_data = parse_extra_banlist(banlist_extra_file)
for tier, conf_file in conf_files.items():
    update_conf_file(conf_file, banlist_data[tier])
