import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_instance import mcp
from db import contacts_dao



@mcp.tool()
def detailsOfperson(name: str):
    """
    Give contact details of people working at IIT Mandi (professors and staff) details like office, email, phone etc,.
    It accepts all types of names (full names, initials, or partial names) and returns
    the best fuzzy-matched contact details from the directory.
    """
    return contacts_dao.fuzzy_search_contact_by_name(name, 0.7, 3)


@mcp.tool()
def detailsBySection(section: str):
    """
    Give contact details of people working at IIT Mandi (professors and staff) based on the section they belong to.
    It accepts partial or full section names (like 'Deans', 'Academic Office', 'Student Affairs', etc.)
    and returns the top fuzzy-matched contact details from the directory.
    """
    return contacts_dao.fuzzy_search_by_section(section, 0.7, 5)



@mcp.tool()
def detailsByDesignationAndSection(designation: str, section: str):
    """
   This tool is designed to retrieve contact details (like email, office, phone, etc.) of people working
    at IIT Mandi, based on a fuzzy match of both:

    1. Designation (e.g., Professor, Dean (Students), Assistant Registrar)

    2. Section (e.g., Academic Section, Health Center, IIT Mandi Catalyst, Suraj Taal Hostel, etc.)

    You can input:

    Partial or full designation

    Partial or full section
    And it will return the most relevant matches ranked by combined similarity.
    """
    return contacts_dao.fuzzy_search_by_designation_and_section(designation, section, 0.7, 5)



