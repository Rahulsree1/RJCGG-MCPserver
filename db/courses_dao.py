import csv
import psycopg2.extras
import Levenshtein
from db import get_connection, return_connection


def create_course_directory_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS instructor (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS course (
                    id SERIAL PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    credits INTEGER,
                    slot TEXT,
                    classroom TEXT,
                    location TEXT,
                    label TEXT,
                    school TEXT,
                    for_students TEXT,
                    additional_info TEXT,
                    instructor_id INTEGER REFERENCES instructor(id) ON DELETE SET NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS slot_schedule (
                    id SERIAL PRIMARY KEY,
                    course_id INTEGER REFERENCES course(id) ON DELETE CASCADE,
                    day TEXT,
                    time_range TEXT
                );
            """)
        conn.commit()
        print("✅ Course tables created.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating course tables: {e}")
    finally:
        return_connection(conn)

def safe_int(val, default=0):
    try:
        return int(val.strip())
    except:
        return default

def insert_courses_from_csv(csv_path: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur, open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                instructor_name = row['Instructor'].strip()
                cur.execute("SELECT id FROM instructor WHERE name = %s", (instructor_name,))
                result = cur.fetchone()
                instructor_id = result[0] if result else None

                if not instructor_id:
                    cur.execute("INSERT INTO instructor (name) VALUES (%s) RETURNING id", (instructor_name,))
                    instructor_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO course (code, name, credits, slot, classroom, location,
                                        label, school, for_students, additional_info, instructor_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    row['Course Code'].strip(),
                    row['Course Name'].strip(),
                    safe_int(row['Credits']),
                    row['Slot'].strip(),
                    row['Classroom'].strip(),
                    row['Location'].strip(),
                    row['Label'].strip(),
                    row['School'].strip(),
                    row['For the Students'].strip() if row['For the Students'] else None,
                    row['Additional Info'].strip() if row['Additional Info'] else None,
                    instructor_id
                ))
                course_id = cur.fetchone()[0]

                # Parse and insert slot schedules
                schedule_parts = [s.strip() for s in row['Slot Schedule'].split(',') if s.strip()]
                for part in schedule_parts:
                    if ' ' in part:
                        day, time_range = part.split(' ', 1)
                        cur.execute("""
                            INSERT INTO slot_schedule (course_id, day, time_range)
                            VALUES (%s, %s, %s)
                        """, (course_id, day, time_range.strip()))

        conn.commit()
        print("✅ Courses inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting course data: {e}")
    finally:
        return_connection(conn)

def create_course_view_table():
    """
    Creates a SQL VIEW named 'course_view' to simplify reads from the normalized courses directory.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE VIEW course_view AS
                SELECT
                    c.id AS course_id,
                    c.code AS course_code,
                    c.name AS course_name,
                    i.name AS instructor_name,
                    c.credits,
                    c.slot,
                    c.classroom,
                    c.location,
                    c.label,
                    c.school,
                    c.for_students,
                    c.additional_info,
                    COALESCE(string_agg(s.day || ' ' || s.time_range, ', ' ORDER BY s.day), '') AS slot_schedule
                FROM course c
                LEFT JOIN instructor i ON c.instructor_id = i.id
                LEFT JOIN slot_schedule s ON c.id = s.course_id
                GROUP BY c.id, i.name;
            """)
        conn.commit()
        print("✅ View 'course_view' created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating course view: {e}")
    finally:
        return_connection(conn)

def get_courses_by_instructor(instructor_name: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM course_view
                WHERE instructor_name ILIKE %s
            """, (f'%{instructor_name}%',))
            return cur.fetchall()
    finally:
        return_connection(conn)

def get_course_by_code(code: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM course_view
                WHERE course_code = %s
            """, (code,))
            return cur.fetchone()
    finally:
        return_connection(conn)

def fuzzy_search_courses_by_field(field: str, value: str, threshold=0.7, limit=5):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(f"SELECT * FROM course_view")
            rows = cur.fetchall()

            search_name = value.strip()
            results = []
            for row in rows:
                
                target = row.get(field)
                if target:
                    score = Levenshtein.ratio(value.lower(), str(target).lower())
                    if score >= threshold:
                        row_dict = dict(row)
                        combined = f"{row_dict.pop('classroom', '')} - {row_dict.pop('location', '')}"
                        row_dict["classroom location"] = combined.strip(" -")
                        results.append({
                            "course_details": row_dict,
                            "matched_word":target,
                            "similarity": round(score, 3)
                        })
                    else:
                        name_parts = target.strip().split()
                        name_initials = ''.join(word[0] for word in name_parts if word)
                        name_variants = name_parts + [name_initials]
                        best_match = None
                        for part in name_variants:
                            ratio = Levenshtein.ratio(search_name.lower(), part.lower())
                            if ratio >= threshold:
                                if not best_match or ratio > best_match["similarity"]:
                                    best_match = {
                                        "Details": dict(row),
                                        "matched_word": part,
                                        "searched_with": search_name,
                                        "similarity": round(ratio, 3)
                                    }
                        if best_match:
                            results.append(best_match)


            return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]
    finally:
        return_connection(conn)

def search_course_by_flexible_code(code_query: str):
    """
    Searches course by code, allowing dashes and case-insensitive match.
    Example: AR511 matches AR-511, ar511, ar-511, etc.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            normalized = code_query.replace("-", "").lower()

            cur.execute("SELECT * FROM course_view")
            results = []
            for row in cur.fetchall():
                db_code = row['course_code'].replace("-", "").lower()
                if db_code == normalized:
                    row_dict = dict(row)
                    combined = f"{row_dict.pop('classroom', '')} - {row_dict.pop('location', '')}"
                    row_dict["classroom location"] = combined.strip(" -")
                    results.append(row_dict)

            return results
    finally:
        return_connection(conn)

def update_course(course_code: str, **kwargs):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            fields = []
            values = []
            for k, v in kwargs.items():
                fields.append(f"{k} = %s")
                values.append(v)
            if not fields:
                return False
            values.append(course_code)
            query = f"UPDATE course SET {', '.join(fields)} WHERE code = %s"
            cur.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating course: {e}")
        return False
    finally:
        return_connection(conn)

def delete_course_by_code(course_code: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM course WHERE code = %s", (course_code,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting course: {e}")
        return False
    finally:
        return_connection(conn)


