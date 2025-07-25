import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_connection, return_connection



def create_mess_menu_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mess_menu (
                    id SERIAL PRIMARY KEY,
                    day TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    items TEXT[] NOT NULL
                );
            """)
        conn.commit()
    finally:
        return_connection(conn)




def find_meal_by_item(item_name: str) -> list[tuple[str, str, str]]:
    """
    Returns (day, meal_type, matched_item) where the item appears as a substring (case-insensitive).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.day, m.meal_type, item
                FROM mess_menu m,
                     unnest(m.items) AS item
                WHERE item ILIKE %s;
            """, (f'%{item_name}%',))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_full_menu() -> list[dict]:
    """
    Returns all mess menu entries as a list of dicts.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT day, meal_type, items FROM mess_menu;
            """)
            rows = cur.fetchall()
            return [{"day": row[0], "meal_type": row[1], "items": row[2]} for row in rows]
    finally:
        return_connection(conn)


def get_items_by_day_and_meal(day: str, meal_type: str) -> list[str]:
    """
    Returns the list of items served on a given day and meal_type.
    Example: get_items_by_day_and_meal('Monday', 'Lunch')
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT items
                FROM mess_menu
                WHERE LOWER(day) = LOWER(%s)
                  AND LOWER(meal_type) = LOWER(%s)
                LIMIT 1;
            """, (day, meal_type))
            result = cur.fetchone()
            return result[0] if result else []
    finally:
        return_connection(conn)





def get_menu_by_day(day: str) -> list[tuple[str, list[str]]]:
    """
    Returns a list of (meal_type, items) for the given day.
    Example: get_menu_by_day('Monday')
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT meal_type, items
                FROM mess_menu
                WHERE LOWER(day) = LOWER(%s)
                ORDER BY meal_type;
            """, (day,))
            return cur.fetchall()  # List of (meal_type, items)
    finally:
        return_connection(conn)







def create_mess_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mess_menu (
                    id SERIAL PRIMARY KEY,
                    day TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    items TEXT[] NOT NULL  -- change here: use TEXT[]
                );
            """)
            conn.commit()
    finally:
        return_connection(conn)





def delete_menu_item(day: str, meal_type: str):
    """
    Deletes the menu for the specified day and meal.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM mess_menu
                WHERE day = %s AND meal_type = %s;
            """, (day, meal_type))
            conn.commit()
    finally:
        return_connection(conn)


def add_menu_row(day: str, meal_type: str, items: list[str]):
    """
    Inserts a new row into the mess_menu table (auto-incrementing id).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mess_menu (day, meal_type, items)
                VALUES (%s, %s, %s);
            """, (day, meal_type, items))
        conn.commit()
    finally:
        return_connection(conn)




def insert_menu_from_json(json_path: str):
    """
    Reads the mess menu JSON file and inserts each row into the mess_menu table.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    for day, meals in menu_data.items():
        for meal_type, items in meals.items():
            # Call your existing function
            add_menu_row(day, meal_type, items)





def add_single_item_to_menu(day: str, meal_type: str, item: str):
    """
    Add a single item to the items array for a given day and meal.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE mess_menu
                SET items = array_append(items, %s)
                WHERE day = %s AND meal_type = %s;
            """, (item, day, meal_type))
            conn.commit()
    finally:
        return_connection(conn)




def delete_single_item_from_menu(day: str, meal_type: str, item: str):
    """
    Remove a single item from the items array for a given day and meal.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE mess_menu
                SET items = array_remove(items, %s)
                WHERE day = %s AND meal_type = %s;
            """, (item, day, meal_type))
            conn.commit()
    finally:
        return_connection(conn)





