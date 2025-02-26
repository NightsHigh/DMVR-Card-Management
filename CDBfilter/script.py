import sqlite3
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def read_card_ids(file_path):
    """Reads card IDs from a .conf file and returns a set of IDs."""
    card_ids = set()
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                match = re.match(r"(\d+) \d # (.+),", line)
                if match:
                    card_id = match.group(1).strip()
                    card_ids.add(card_id)
    except FileNotFoundError:
        logging.error(f"Error: {file_path} not found!")
    return card_ids

def update_card_labels(database_paths, red_conf, blue_conf, white_conf, error_log_file):
    """Updates the OT field in the databases based on card IDs from .conf files."""
    # Read card IDs instead of names
    red_card_ids = read_card_ids(red_conf)   # Should be OT = 8 (ILLEGAL)
    blue_card_ids = read_card_ids(blue_conf) # Should be OT = 2 (TCG)
    white_card_ids = read_card_ids(white_conf) # Should be OT = 32 (CUSTOM)

    all_listed_cards = red_card_ids | blue_card_ids | white_card_ids  # Combine all IDs

    if not all_listed_cards:
        logging.error("No card IDs found. Aborting update.")
        return

    for db_path in database_paths:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Step 1: Hide all unlisted cards (OT = 4096)
            logging.info(f"Hiding all unlisted cards in {db_path} by setting OT = 4096...")
            cursor.execute(f"""
                UPDATE datas SET ot = 4096 WHERE id NOT IN ({','.join('?' * len(all_listed_cards))})
            """, tuple(all_listed_cards))
            logging.info(f"Updated {cursor.rowcount} unlisted cards to OT = 4096.")

            # Step 2: Update OT for listed cards
            logging.info(f"Updating OT for Red, Blue, and White cards in {db_path}...")

            if red_card_ids:
                cursor.executemany("UPDATE datas SET ot = 8 WHERE id = ?", [(card_id,) for card_id in red_card_ids])
                logging.info(f"Updated {len(red_card_ids)} RED cards to ILLEGAL (8).")

            if blue_card_ids:
                cursor.executemany("UPDATE datas SET ot = 2 WHERE id = ?", [(card_id,) for card_id in blue_card_ids])
                logging.info(f"Updated {len(blue_card_ids)} BLUE cards to TCG (2).")

            if white_card_ids:
                cursor.executemany("UPDATE datas SET ot = 32 WHERE id = ?", [(card_id,) for card_id in white_card_ids])
                logging.info(f"Updated {len(white_card_ids)} WHITE cards to CUSTOM (32).")

            conn.commit()
            logging.info(f"Database update complete for {db_path}!")

        except sqlite3.Error as e:
            logging.error(f"Database error in {db_path}: {e}")
        finally:
            conn.close()

# Define file paths
database_paths = ["cards.cdb", "cards-unofficial.cdb", "goat-entries.cdb"]  # List of databases to search
red_conf = "OnlyRedCards.conf"
blue_conf = "OnlyBlueCards.conf"
white_conf = "OnlyWhiteCards.conf"
error_log_file = "unmatched_cards.txt"  # File to log unmatched card names

# Run the update
update_card_labels(database_paths, red_conf, blue_conf, white_conf, error_log_file)
