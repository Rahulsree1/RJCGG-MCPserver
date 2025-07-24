import Levenshtein
import sqlite3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_instance import mcp


def search_fuzzy_name_columns_sorted(db_path, search_value, threshold=0.7):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = []
    table_name = "ContactDetails"

    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    col_info = cursor.fetchall()
    name_columns = [col[1] for col in col_info if col[1].lower() == 'name']

    # Fetch all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Prepare search parts
    search_value = search_value.strip()
    search_parts = search_value.split()
    search_initials = ''.join(word[0] for word in search_parts if word)
    search_variants = search_parts

    for row in rows:
        row_dict = dict(row)
        if row_dict["Email"]: row_dict['Email'] += '@iitmandi.ac.in'
        for col in name_columns:
            cell_value = row_dict.get(col)
            if isinstance(cell_value, str):
                full_name = cell_value.strip()
                full_ratio = Levenshtein.ratio(search_value.lower(), full_name.lower())

                # First try full name match with high threshold
                if full_ratio >= 0.9:
                    results.append({
                        "Details": row_dict,
                        "matched_word": full_name,
                        "similarity": round(full_ratio, 3)
                    })
                else:
                    # Prepare name parts and initials
                    name_parts = full_name.split()
                    name_initials = ''.join(word[0] for word in name_parts if word)
                    name_variants = name_parts
                    name_variants.append(name_initials)

                    best_match = None
                    for n in name_variants:
                        ratio = Levenshtein.ratio(search_value.lower(), n.lower())
                        if ratio >= threshold:
                            if not best_match or ratio > best_match["similarity"]:
                                
                                best_match = {
                                    "Details": row_dict,
                                    "matched_word": n,
                                    "searched_with": search_value,
                                    "similarity": round(ratio, 3)
                                }
                    if best_match:
                        results.append(best_match)

    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results[:3] if len(results) > 3 else results



@mcp.tool()
def infoOfperson(name: str):
    """Give contact details of people working at IIT Mandi,
      Professor's and staff, it takes only the name of person as augument.
        it for all types of names"""

    return search_fuzzy_name_columns_sorted("./condatabase.db", name)