import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import re
from collections import defaultdict

import re
from collections import defaultdict

def normalize_section(section: str) -> str:
    """Normalize section names by cleaning spaces and replacing special characters."""
    section = section.replace("&", "and")
    section = re.sub(r"\s+", " ", section)  # collapse multiple spaces
    return section.strip()

def merge_contacts_sorted_by_designation(contact_list):
    merged = {}

    for contact in contact_list:
        details = contact["Details"]
        person_id = details["person_id"]

        if person_id not in merged:
            merged[person_id] = {
                "person_id": person_id,
                "name": details["name"],
                "roles": defaultdict(lambda: {
                    "emails": set(),
                    "offices": set(),
                    "phones": set(),
                    "sections": set()
                }),
                "matched_word": contact.get("matched_word"),
                "similarity": contact.get("similarity")
            }

        role = merged[person_id]["roles"][details["designation"]]
        role["emails"].add(str(details["email"]))
        role["offices"].add(str(details["office"]))
        role["phones"].add(str(details["phone"]))
        role["sections"].add(normalize_section(str(details["section"])))

    # Final transformation: sets → lists and sort roles by designation
    for person in merged.values():
        person["roles"] = sorted([
            {
                "designation": designation,
                "emails": sorted(role_data["emails"]),
                "offices": sorted(role_data["offices"]),
                "phones": sorted(role_data["phones"]),
                "sections": sorted(role_data["sections"])
            }
            for designation, role_data in merged[person["person_id"]]["roles"].items()
        ], key=lambda r: r["designation"].lower())  # sort by designation

    return list(merged.values())
