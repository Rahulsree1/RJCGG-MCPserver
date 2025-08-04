import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_instance import mcp
from db import courses_dao


@mcp.tool()
def get_course_by_name_fuzzy(courseName: str):
    """
    Retrieve detailed course information at IIT Mandi based on a fuzzy match of the course name.

    This function supports:
    - Full course names (e.g., "Data Handling and Visualisation")
    - Partial names (e.g., "Handling", "Visualisation")
    - Abbreviations or acronyms (e.g., "DHAV" for "Data Handling and Visualisation")
    - Common short forms or typos (e.g., "dhv")

    Fuzzy search allows approximate matching, so even imprecise input can return relevant results.

    Returns:
        A JSON object with:
        - "Details": A dictionary containing full course information:
          - Course ID
          - Course Code and Name
          - Instructor Name
          - Credits
          - Slot, Classroom, and Location (if available)
          - Timings of course and Other Metadata
    """

    retrivedData = courses_dao.fuzzy_search_courses_by_field('course_name', courseName, 0.5, 3)

    return "No data has been found for given course name" if len(retrivedData) == 0  else retrivedData



@mcp.tool()
def get_course_by_code(course_code: str):
    """
    Retrieve course details at IIT Mandi based on the provided course code.

    Supports flexible matching (e.g., IC112, ic 112, IC-112).
    The function returns key information such as:
    - Course ID
    - Course Code and Name
    - Instructor Name
    - Credits
    - Slot, Classroom, and Location (if available)
    - Timings of course and Other Metadata

    Example input:
        "IC112"

    """

    retrivedData = courses_dao.search_course_by_flexible_code(course_code.strip())

    return "No data has been found for given course code" if len(retrivedData) == 0  else retrivedData



@mcp.tool()
def get_course_by_instructure_name(name: str):
    """
    Retrieve course details at IIT Mandi based on the provided Instructor name.

    This function supports all types of name inputs:
        - Full names (e.g., "Subajith Roy Chowdhury")
        - Initials (e.g., "G. Shrikanth Reddy")
        - Partial names (e.g., "Shrikanth", "Roy")
        - Abbreviations or acronyms (e.g., "GSR" for "G. Shrikanth Reddy", "SRC" for "Subajith Roy Chowdhury")
    The function returns key information such as:
    - Course ID
    - Course Code and Name
    - Instructor Name
    - Credits
    - Slot, Classroom, and Location (if available)
    - Timings of course and Other Metadata

    """

    retrivedData = courses_dao.search_course_by_flexible_code(name.strip())

    return "No data has been found for given instructor name" if len(retrivedData) == 0  else retrivedData



# @mcp.tool()
# def get_course_by_schedule():
#     pass


# @mcp.tool()
# def get_schedule_by_slot():
#     pass



