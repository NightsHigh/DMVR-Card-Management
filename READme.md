# Card Sorting and EDOPro Banlist Integration

## Overview
This project processes card data from a CSV file and a banlist file to categorize and integrate them into the EDOPro system. It assigns colors to cards based on their type and ensures they are correctly marked in EDOPro's database and banlist.

## Features
- Extracts and categorizes cards into:
  - **Red Cards** (Ultimate) - Marked as illegal
  - **Blue Cards** (Super) - Marked as TCG
  - **White Cards** (Remaining) - Marked as CSTM (Custom)
- Searches an API and EDOPro database files (official and unofficial) to fill in missing card data.
- Converts EDOPro databases to reflect the new categorization.
- Supports a custom DMVR banlist that enables both color-coded cards and banlist restrictions in EDOPro.

## Installation
1. Clone this repository:
   ```sh
   git clone <repository_url>
   ```
2. Install required dependencies (if any):
   ```sh
   pip install -r requirements.txt
   ```
3. Ensure you have access to the necessary CSV and banlist files.

## Usage
1. Place the required CSV and banlist files in the appropriate directories.
2. Run the main processing script:
   ```sh
   python main.py
   ```
3. The script will generate three sorted files:
   - `red_cards.csv`
   - `blue_cards.csv`
   - `white_cards.csv`
4. These files are then processed and integrated into EDOPro's database and banlist system.

## Output
- Updated EDOPro database with categorized cards.
- A custom banlist displaying numbers according to the DMVR system.
- Properly colored cards based on classification.

## License
This project is released under an open-source license for the code. However, please note:
- This project is a fan-made tool and is not affiliated with, endorsed by, or sponsored by Konami.
- Yu-Gi-Oh! and all related images, cards, and trademarks belong to Konami.
- Users must obtain the necessary assets legally and ensure compliance with copyright laws.

For open-source licensing, this project follows the **MIT License** for the codebase.

