import sys
import os

import db.mess_dao
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import db


from mcp_instance import mcp



@mcp.tool()
def get_menu_by_day_and_meal_type(day: str, meal_type: str):


    """
    Retrieves the mess menu for IIT Mandi cafeteria/dining hall for a specific day and meal type.
    
    Args:
        day (str): The day of the week for which to get the menu.
                  Expected values: "monday", "tuesday", "wednesday", "thursday",
                  "friday", "saturday", "sunday" (case-insensitive)
                  
        meal_type (str): The type of meal to retrieve menu for.
                        Expected values: "breakfast", "lunch", "dinner", "snacks"
    
    Returns:
        str: A formatted string containing the menu items for the specified day and meal type.
             Returns food items like rice, dal, vegetables, roti, curry, etc.
             If no menu found, returns appropriate message.
    
    Example:
        >>> get_menu_by_day_and_mealtype("monday", "lunch")
        "here are the mess menu: Rice, Dal Tadka, Mixed Vegetable, Roti, Pickle, Curd"
        
        >>> get_menu_by_day_and_mealtype("friday", "dinner")
        "here are the mess menu: Jeera Rice, Rajma, Aloo Gobi, Chapati, Papad, Salad"
    Note:
        - This function queries the IIT Mandi mess database for current menu items
        - Menu items are typically Indian cuisine suitable for vegetarian and non-vegetarian students
        - The mess operates on a weekly rotating menu schedule
        - Function is case-insensitive for both day and meal_type parameters
    """

    day = day.lower().strip()
    meal_type = meal_type.lower().strip()
    
    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if day not in valid_days:
        return f"Invalid day '{day}'. Please use one of: {', '.join(valid_days)}"
    

    valid_meals = ["breakfast", "lunch", "dinner", "snacks"]
    if meal_type not in valid_meals:
        return f"Invalid meal type '{meal_type}'. Please use one of: {', '.join(valid_meals)}"
    
    try:
        res = db.mess_dao.get_items_by_day_and_meal(day, meal_type)
        
        if res:
            return f"Here is the mess menu for {day.title()} {meal_type.title()}: {res}, format it present it little emoji touch"
        else:
            return f"No menu found for {day.title()} {meal_type.title()}. Please check with mess administration."
            
    except Exception as e:
        return f"Error retrieving menu: {str(e)}. Please try again later."




@mcp.tool()
def         get_days_by_item(items:list):



    pass


