import os
import json
import re

# Load card data from JSON file
card_data_path = 'cardData.json'
with open(card_data_path, 'r') as f:
    card_data = json.load(f)

# Regular expression to remove suffixes like (Manga), (Anime), (VG)
suffix_pattern = re.compile(r'\s*\((manga|anime|vg)\)', re.IGNORECASE)

# Create a dictionary to map normalized card names to card IDs
name_to_id = {}
for card in card_data:
    # Remove suffixes like (Manga), (Anime), (VG) from card names
    normalized_name = re.sub(suffix_pattern, '', card['name']).strip().lower()
    name_to_id[normalized_name] = str(card['id']).strip()

# Define the directory containing the images
directory = 'DMVR Erratas'

# List all files for debugging
all_files = os.listdir(directory)
print(f"All files in directory: {all_files}")  # Debugging: List all files

# Iterate over each file in the directory
for filename in all_files:
    # Get the file name without extension
    name, ext = os.path.splitext(filename)

    # Skip non-image files (only handle .jpg and .png)
    if ext.lower() not in ['.jpg', '.png']:
        continue

    # Normalize the name for matching (remove spaces, convert to lowercase)
    normalized_name = name.strip().lower()

    # Debugging: Log the current file being processed
    print(f"Processing file: {filename} (normalized: {normalized_name})")

    # Check if the card name exists in the JSON data
    card_id = name_to_id.get(normalized_name)
    if card_id:
        # Create the new file name with the card ID, always using .png extension
        new_filename = f"{card_id}.png"
        old_filepath = os.path.join(directory, filename)
        new_filepath = os.path.join(directory, new_filename)

        # Rename the file if needed (if the name contains spaces or is different)
        if old_filepath != new_filepath:
            os.rename(old_filepath, new_filepath)
            print(f"Renamed '{filename}' to '{new_filename}'")
        else:
            print(f"Verified '{filename}' is correctly named.")
    else:
        print(f"No matching entry found for card name '{name}', skipping...")

# Debugging: Log completion of script
print("Renaming process completed.")
