import re

# Mapping restriction levels to numbers
BANLIST_MAPPING = {
    "Forbidden": "0",
    "Limited": "1",
    "Semi-Limited": "2",
    "Unlimited": "3"
}

def parse_banlist(banlist_file):
    """Extracts card names and their restriction levels from the banlist file."""
    banlist = {}
    with open(banlist_file, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("\t")  # Assuming tab-separated values
            if len(parts) >= 4:
                card_name = parts[2].strip()
                restriction = BANLIST_MAPPING.get(parts[3].strip(), "3")
                banlist[card_name] = restriction
    return banlist

def update_conf_file(conf_file, banlist):
    """Updates a .conf file with new restriction levels based on the banlist."""
    updated_lines = []
    with open(conf_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r"(\d+) \d # (.+),", line)
            if match:
                card_id, card_name = match.groups()
                restriction = banlist.get(card_name, "3")  # Default to 3 (Unlimited)
                updated_lines.append(f"{card_id} {restriction} # {card_name},\n")
            else:
                updated_lines.append(line)
    
    # Write updated content back to file
    with open(conf_file, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

def main():
    banlist_file = "Banlist.txt"
    conf_files = ["OnlyWhiteCards.conf", "OnlyRedCards.conf", "OnlyBlueCards.conf"]
    
    # Parse the banlist file
    banlist = parse_banlist(banlist_file)
    
    # Update each conf file
    for conf_file in conf_files:
        update_conf_file(conf_file, banlist)
    
    print("Conf files updated successfully.")

if __name__ == "__main__":
    main()
