import re
import logging

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

def remove_blue_from_white(blue_conf, white_conf):
    """Removes any cards in Blue from White."""
    blue_card_ids = read_card_ids(blue_conf)
    updated_lines = []
    try:
        with open(white_conf, "r", encoding="utf-8") as file:
            for line in file:
                match = re.match(r"(\d+) \d # (.+),", line)
                if match and match.group(1).strip() in blue_card_ids:
                    continue  # Skip Blue cards in White list
                updated_lines.append(line.strip())
    except FileNotFoundError:
        logging.error(f"Error: {white_conf} not found!")
        return
    
    with open(white_conf, "w", encoding="utf-8") as file:
        file.write("\n".join(updated_lines) + "\n")
    logging.info(f"Removed {len(blue_card_ids)} duplicate Blue cards from {white_conf}.")

# Define file paths
blue_conf = "OnlyBlueCards.conf"
white_conf = "OnlyWhiteCards.conf"

# Run the cleanup
remove_blue_from_white(blue_conf, white_conf)
