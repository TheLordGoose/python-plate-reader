import re

# Function to normalize plate inputs ensuring we're reducing duplicates .etc.
def normalize_plate(plate: str) -> str:
    # Standardizes the plate by removing spaces and converting to uppercase.
    return re.sub(r"[^A-Z0-9]", "", plate.upper().strip())

# Function setup to handle different plate types
def is_valid_uk_plate(plate: str) -> bool:
    normalized_plate = normalize_plate(plate)
    print(f"Checking plate: {normalized_plate}")

    patterns = [
        r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$",     # Post-2001: AB12 XYZ
        r"^[A-Z][0-9]{1,3}[A-Z]{3}$",      # Prefix: A123 ABC
        r"^[A-Z]{3}[0-9]{1,3}[A-Z]?$",     # Suffix: ABC 123 D
        r"^[A-Z0-9]{3,8}$",                # Dateless/vanity
    ]

    for pattern in patterns:
        if re.fullmatch(pattern, normalized_plate):
            print(f"Plate matched pattern: {pattern}")
            return True

    print("No match found for the plate.")
    return False