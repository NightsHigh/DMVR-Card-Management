import json
import sys

def load_card_data(json_file):
    """Load the card name-to-ID mapping from cardData.json."""
    with open(json_file, 'r', encoding='utf-8') as f:
        card_data = json.load(f)
    return {card["name"]: card["id"] for card in card_data}

def load_extra_deck_names(file_path):
    """Load extra deck card names from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}

def filter_file(extra_deck_file, card_data_file, target_files):
    """Remove lines from multiple target files that contain extra deck card IDs."""
    # Load name-to-ID mapping
    name_to_id = load_card_data(card_data_file)
    
    # Load extra deck card names and find their corresponding IDs
    extra_deck_names = load_extra_deck_names(extra_deck_file)
    extra_deck_ids = {name_to_id[name] for name in extra_deck_names if name in name_to_id}

    for target_file in target_files:
        output_file = target_file.replace(".conf", "_filtered.conf")

        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open(output_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if not any(card_id in line for card_id in extra_deck_ids):
                    f.write(line)

        print(f"Filtered file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python remove_extra_deck_from_all.py extracted_extra_deck.txt cardData.json file1.conf file2.conf file3.conf")
        sys.exit(1)

    extra_deck_file = sys.argv[1]  # List of extra deck card names
    card_data_file = sys.argv[2]   # JSON file with name-to-ID mapping
    target_files = sys.argv[3:]    # List of banlist files to filter

    filter_file(extra_deck_file, card_data_file, target_files)
