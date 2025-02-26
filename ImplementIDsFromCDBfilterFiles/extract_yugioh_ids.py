import requests
import os
import time
import re
import sqlite3

def clean_card_name(card_name):
    """
    Remove unwanted designations from the card name.
    This removes any substring in parentheses if it contains one of the unwanted tokens.
    """
    unwanted = r"(Anime|Manga|VG|Video Game|Alternative Artwork)"
    cleaned = re.sub(r"\s*\(" + unwanted + r"\)", "", card_name, flags=re.IGNORECASE)
    return cleaned.strip()

def get_card_id_from_ygoprodeck(card_name):
    """
    Query the YGOPRODeck API using the cleaned card name.
    First, try an exact match using the 'name' parameter.
    If that fails (HTTP != 200 or no data), try a fuzzy search using the 'fname' parameter.
    Returns the card's ID if found, otherwise None.
    """
    cleaned_name = clean_card_name(card_name)
    
    url_exact = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={requests.utils.quote(cleaned_name)}"
    try:
        response = requests.get(url_exact)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                return data["data"][0].get("id")
        else:
            print(f"Exact search failed for '{card_name}' (cleaned: '{cleaned_name}'): HTTP {response.status_code}")
    except Exception as e:
        print(f"Exception during exact search for '{card_name}': {e}")

    url_fuzzy = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={requests.utils.quote(cleaned_name)}"
    try:
        response = requests.get(url_fuzzy)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                return data["data"][0].get("id")
        else:
            print(f"Fuzzy search failed for '{card_name}' (cleaned: '{cleaned_name}'): HTTP {response.status_code}")
    except Exception as e:
        print(f"Exception during fuzzy search for '{card_name}': {e}")

    return None

def get_card_id_from_ignis(card_name):
    """
    Attempt to retrieve the card's ID from the Project Ignis database.
    Tries both 'cards.cdb' and 'cards-unofficial.cdb'.
    """
    ignis_db_files = [
        "/home/soeren/.local/opt/edopro/app/expansions/cards.cdb",
        "/home/soeren/.local/opt/edopro/app/expansions/cards-unofficial.cdb"
    ]
    
    cleaned_name = clean_card_name(card_name)
    
    for db_file in ignis_db_files:
        if not os.path.exists(db_file):
            continue  # Skip if the database file does not exist

        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM texts WHERE name = ?", (cleaned_name,))
            row = cursor.fetchone()
            if row:
                print(f"Found '{card_name}' in {db_file} with ID: {row[0]}")
                return row[0]
        except Exception as e:
            print(f"Error querying {db_file} for '{card_name}': {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    return None

def get_card_id(card_name):
    """
    Attempt to retrieve the card's ID.
    Try YGOPRODeck first; if not found, fall back to Project Ignis databases.
    """
    card_id = get_card_id_from_ygoprodeck(card_name)
    if card_id is None:
        card_id = get_card_id_from_ignis(card_name)
    if card_id is None:
        print(f"Card ID not found for: '{card_name}'")
    return card_id

def process_cards(input_filename, output_filename):
    """
    Read card names from the input file, fetch their IDs using YGOPRODeck and Project Ignis,
    and write them to the output file in the format: <cardID> 1 # <Card Name>.
    """
    not_found_cards = []
    if not os.path.exists(input_filename):
        print(f"Input file {input_filename} not found!")
        return not_found_cards

    output_lines = []
    with open(input_filename, "r", encoding="utf-8") as file:
        for line in file:
            card_name = line.strip()
            if not card_name:
                continue
            card_id = get_card_id(card_name)
            if card_id:
                output_lines.append(f"{card_id} 1 # {card_name},")
            else:
                not_found_cards.append(card_name)
            time.sleep(0.2)  # Respect API rate limits

    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines))
    print(f"Processed {len(output_lines)} cards from '{input_filename}' into '{output_filename}'")
    return not_found_cards

def main():
    files = [
        ("OnlyRedCards.txt", "OnlyRedCards.conf"),
        ("OnlyBlueCards.txt", "OnlyBlueCards.conf"),
        ("OnlyWhiteCards.txt", "OnlyWhiteCards.conf")
    ]
    
    all_not_found = []
    for input_file, output_file in files:
        not_found = process_cards(input_file, output_file)
        all_not_found.extend(not_found)
    
    if all_not_found:
        not_found_file = "cards_not_found.txt"
        with open(not_found_file, "w", encoding="utf-8") as nf:
            nf.write("\n".join(all_not_found))
        print(f"{len(all_not_found)} cards were not found. See '{not_found_file}'.")
    else:
        print("All cards were found.")

if __name__ == "__main__":
    main()
