import sys
import os

import db.mess_dao
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import db

from fastmcp import FastMCP

mcp = FastMCP(name="Mess-Deatils")


@mcp.tool()
def get_menu_by_day_and_mealtype(day:str, meal_type:str):
    """Gives the mess menu of IIT Mandi
     given day and meal_type"""
    
    db.mess_dao.get_items_by_day_and_meal()
    

    return f"here are the messmenhu {}"


#messmenu
#contact deatil 

#busSchedule

    

    
    

