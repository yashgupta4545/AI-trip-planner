"""Dataset validation script using Pydantic schemas."""

import csv
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_validation import DestinationSchema, AttractionSchema
from src.config import DESTINATIONS_FILE, ATTRACTIONS_FILE, BUDGET_ESTIMATES_FILE


def validate_destinations():
    print(f"Validating {DESTINATIONS_FILE}...")
    errors = []
    total = 0
    with open(DESTINATIONS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            total += 1
            # Convert types
            try:
                row_copy = dict(row)
                row_copy["latitude"] = float(row["latitude"])
                row_copy["longitude"] = float(row["longitude"])
                row_copy["recommended_duration_days"] = int(row["recommended_duration_days"])
                row_copy["estimated_daily_budget_inr"] = float(row["estimated_daily_budget_inr"])
                if "accommodation_budget_per_night" in row:
                    row_copy["accommodation_budget_per_night"] = float(row["accommodation_budget_per_night"])
                if "food_budget_per_person_per_day" in row:
                    row_copy["food_budget_per_person_per_day"] = float(row["food_budget_per_person_per_day"])
                if "local_transport_budget_per_day" in row:
                    row_copy["local_transport_budget_per_day"] = float(row["local_transport_budget_per_day"])
                if "sightseeing_budget_per_person_per_day" in row:
                    row_copy["sightseeing_budget_per_person_per_day"] = float(row["sightseeing_budget_per_person_per_day"])
                row_copy["family_friendly"] = row["family_friendly"].lower() in ("true", "1", "yes")
                row_copy["solo_friendly"] = row["solo_friendly"].lower() in ("true", "1", "yes")
                DestinationSchema(**row_copy)
            except Exception as e:
                errors.append(f"Row {i} ({row.get('destination_name', 'Unknown')}): {e}")

    print(f"Validated {total} destinations. Errors found: {len(errors)}")
    if errors:
        for err in errors[:10]:
            print(f"  - {err}")
        return False
    return True


def validate_attractions():
    print(f"Validating {ATTRACTIONS_FILE}...")
    errors = []
    total = 0
    with open(ATTRACTIONS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            total += 1
            try:
                row_copy = dict(row)
                row_copy["typical_duration_hours"] = float(row["typical_duration_hours"])
                row_copy["estimated_ticket_inr"] = float(row["estimated_ticket_inr"])
                if "adult_ticket_price" in row:
                    row_copy["adult_ticket_price"] = float(row["adult_ticket_price"])
                if "child_ticket_price" in row:
                    row_copy["child_ticket_price"] = float(row["child_ticket_price"])
                AttractionSchema(**row_copy)
            except Exception as e:
                errors.append(f"Row {i} ({row.get('attraction_name', 'Unknown')}): {e}")

    print(f"Validated {total} attractions. Errors found: {len(errors)}")
    if errors:
        for err in errors[:10]:
            print(f"  - {err}")
        return False
    return True


if __name__ == "__main__":
    v_dest = validate_destinations()
    v_attr = validate_attractions()
    if v_dest and v_attr:
        print("\nAll datasets passed validation!")
        sys.exit(0)
    else:
        print("\nDataset validation failed!")
        sys.exit(1)
