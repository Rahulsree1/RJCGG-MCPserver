import csv
from db import get_connection, return_connection


def create_normalized_contact_directory_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS person (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contact_info (
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
                    designation TEXT,
                    email TEXT,
                    office TEXT,
                    phone TEXT,
                    section TEXT
                );
            """)
            # Add indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_designation ON contact_info(designation);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_email ON contact_info(email);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_office ON contact_info(office);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_phone ON contact_info(phone);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_section ON contact_info(section);")

        conn.commit()
        print("✅ Tables created successfully with indexes.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
    finally:
        return_connection(conn)



def insert_normalized_directory_csv(csv_path: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur, open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row['name'].strip()

                # Parse row-wise fields
                def parse_array(field: str) -> list[str]:
                    return [item.strip() for item in row[field].split(';') if item.strip()] if row[field].strip() else []

                designations = parse_array('designation')
                emails = parse_array('email')
                offices = parse_array('office')
                phones = parse_array('Phone(Extention)')
                sections = parse_array('school/section')

                # Ensure all lists are of equal length
                max_len = max(len(designations), len(emails), len(offices), len(phones), len(sections))
                pad = lambda lst: lst + [None] * (max_len - len(lst))
                designations = pad(designations)
                emails = pad(emails)
                offices = pad(offices)
                phones = pad(phones)
                sections = pad(sections)

                # Get or create person
                cur.execute("SELECT id FROM person WHERE name = %s", (name,))
                result = cur.fetchone()
                if result:
                    person_id = result[0]
                else:
                    cur.execute("INSERT INTO person (name) VALUES (%s) RETURNING id", (name,))
                    person_id = cur.fetchone()[0]

                # Insert individual contact info entries
                for d, e, o, p, s in zip(designations, emails, offices, phones, sections):
                    cur.execute("""
                        INSERT INTO contact_info (person_id, designation, email, office, phone, section)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (person_id, d, e, o, p, s))

        conn.commit()
        print("✅ Normalized contact data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting CSV data: {e}")
    finally:
        return_connection(conn)


def create_view_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE VIEW contact_directory_view AS
                SELECT
                    p.id AS person_id,
                    p.name,
                    c.designation,
                    c.email,
                    c.office,
                    c.phone,
                    c.section
                FROM person p
                JOIN contact_info c ON p.id = c.person_id
                WHERE p.name IS NOT NULL AND c.designation IS NOT NULL;
            """)
        conn.commit()
        print("✅ View created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating view: {e}")
    finally:
        return_connection(conn)



def get_contacts_by_name(name: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM contact_directory_view
                WHERE name ILIKE %s
            """, (name,))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_contacts_by_designation(designation: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM contact_directory_view
                WHERE designation ILIKE %s
            """, (designation,))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_contacts_by_section(section: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM contact_directory_view
                WHERE section ILIKE %s
            """, (section,))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_contacts_by_office(office: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM contact_directory_view
                WHERE office ILIKE %s
            """, (office,))
            return cur.fetchall()
    finally:
        return_connection(conn)


import psycopg2.extras
import Levenshtein

def fuzzy_search_contact_by_name(search_name: str, threshold=0.7, limit=3):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM contact_directory_view")
            rows = cur.fetchall()

            results = []
            search_name = search_name.strip()



            for row in rows:
                row_dict = dict(row)

                # Auto-append domain if needed
                if row_dict.get("email") and '@' not in row_dict["email"]:
                    row_dict["email"] = ', '.join([ i + "@iitmandi.ac.in" for i in row_dict["email"].split(',')])

                full_name = row_dict.get("name", "").strip()
                full_ratio = Levenshtein.ratio(search_name.lower(), full_name.lower())

                if full_ratio >= 0.9:
                    results.append({
                        "Details": row_dict,
                        "matched_word": full_name,
                        "similarity": round(full_ratio, 3)
                    })
                else:
                    name_parts = full_name.split()
                    name_initials = ''.join(word[0] for word in name_parts if word)
                    name_variants = name_parts + [name_initials]

                    best_match = None
                    for part in name_variants:
                        ratio = Levenshtein.ratio(search_name.lower(), part.lower())
                        if ratio >= threshold:
                            if not best_match or ratio > best_match["similarity"]:
                                best_match = {
                                    "Details": row_dict,
                                    "matched_word": part,
                                    "searched_with": search_name,
                                    "similarity": round(ratio, 3)
                                }
                    if best_match:
                        results.append(best_match)

            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
    finally:
        return_connection(conn)

    


def fuzzy_search_by_designation(designation: str, threshold=0.7, limit=3):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM contact_directory_view")
            rows = cur.fetchall()

            results = []
            for row in rows:
                desig = row["designation"]
                if desig:
                    score = Levenshtein.ratio(designation.lower(), desig.lower())
                    if score >= threshold:
                        row_dict = dict(row)
                        if row_dict.get("email") and '@' not in row_dict["email"]:
                            row_dict["email"] = ', '.join([ i + "@iitmandi.ac.in" for i in row_dict["email"].split(',')])
                        results.append({
                            "match": row_dict,
                            "similarity": round(score, 3)
                        })

            return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        return_connection(conn)


def fuzzy_search_by_section(section: str, threshold=0.7, limit=3):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM contact_directory_view")
            rows = cur.fetchall()

            results = []
            for row in rows:
                sect = row["section"]
                if sect:
                    score = Levenshtein.ratio(section.lower(), sect.lower())
                    if score >= threshold:
                        row_dict = dict(row)
                        if row_dict.get("email") and '@' not in row_dict["email"]:
                            row_dict["email"] = ', '.join([ i + "@iitmandi.ac.in" for i in row_dict["email"].split(',')])
                        results.append({
                            "match": row_dict,
                            "similarity": round(score, 3)
                        })

            return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        return_connection(conn)


def fuzzy_search_by_designation_and_section(designation: str, section: str, threshold=0.7, limit=5):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM contact_directory_view")
            rows = cur.fetchall()

            results = []
            for row in rows:
                desig = row["designation"]
                sect = row["section"]
                if desig and sect:
                    desig_score = Levenshtein.ratio(designation.lower(), desig.lower())
                    sect_score = Levenshtein.ratio(section.lower(), sect.lower())
                    avg_score = (desig_score + sect_score) / 2

                    if avg_score >= threshold:
                        row_dict = dict(row)
                        if row_dict.get("email") and '@' not in row_dict["email"]:
                            row_dict["email"] = ', '.join([ i + "@iitmandi.ac.in" for i in row_dict["email"].split(',')])
                        results.append({
                            "match": row_dict,
                            "similarity": round(avg_score, 3),
                            "designation_similarity": round(desig_score, 3),
                            "section_similarity": round(sect_score, 3)
                        })

            return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        return_connection(conn)




def filter_contacts(name=None, designation=None, section=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            conditions = []
            values = []
            if name:
                conditions.append("name ILIKE %s")
                values.append(name)
            if designation:
                conditions.append("designation ILIKE %s")
                values.append(designation)
            if section:
                conditions.append("section ILIKE %s")
                values.append(section)

            query = "SELECT * FROM contact_directory_view"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cur.execute(query, values)
            return cur.fetchall()
    finally:
        return_connection(conn)


def add_contact(name: str, designation: str, email: str, phone: str, office: str, section: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if person exists
            cur.execute("SELECT id FROM person WHERE name ILIKE %s", (name,))
            person = cur.fetchone()
            if person:
                person_id = person[0]
            else:
                cur.execute("INSERT INTO person (name) VALUES (%s) RETURNING id", (name,))
                person_id = cur.fetchone()[0]

            # Insert into contact_info
            cur.execute("""
                INSERT INTO contact_info (person_id, designation, email, phone, office, section)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (person_id, designation, email, phone, office, section))

            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding contact: {e}")
        return False
    finally:
        return_connection(conn)


def update_contact(contact_id: int, designation=None, email=None, phone=None, office=None, section=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            updates = []
            values = []
            if designation:
                updates.append("designation = %s")
                values.append(designation)
            if email:
                updates.append("email = %s")
                values.append(email)
            if phone:
                updates.append("phone = %s")
                values.append(phone)
            if office:
                updates.append("office = %s")
                values.append(office)
            if section:
                updates.append("section = %s")
                values.append(section)

            if not updates:
                return False  # Nothing to update

            values.append(contact_id)
            query = f"UPDATE contact_info SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating contact: {e}")
        return False
    finally:
        return_connection(conn)


def delete_contact(contact_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contact_info WHERE id = %s", (contact_id,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting contact: {e}")
        return False
    finally:
        return_connection(conn)


def delete_person(name: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM person WHERE name ILIKE %s", (name,))
            pid = cur.fetchone()
            if not pid:
                return False

            # Delete all contact_info rows first
            cur.execute("DELETE FROM contact_info WHERE person_id = %s", (pid[0],))
            # Then delete the person
            cur.execute("DELETE FROM person WHERE id = %s", (pid[0],))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting person: {e}")
        return False
    finally:
        return_connection(conn)
