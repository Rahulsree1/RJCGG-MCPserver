import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_instance import mcp
from db import contacts_dao
from tools.contacts.functions import merge_contacts_sorted_by_designation

@mcp.tool()
def detailsOfperson(name: str):
    """
        Give contact details of professors and staff at IIT Mandi, including office location, email, phone number, and more.

        This function supports all types of name inputs:
        - Full names (e.g., "Subajith Roy Chowdhury")
        - Initials (e.g., "G. Shrikanth Reddy")
        - Partial names (e.g., "Shrikanth", "Roy")
        - Abbreviations or acronyms (e.g., "GSR" for "G. Shrikanth Reddy", "SRC" for "Subajith Roy Chowdhury")

        It performs fuzzy matching to return the best-matched contact information from the institute directory.

    """

    return merge_contacts_sorted_by_designation(contacts_dao.fuzzy_search_contact_by_name(name, 0.5, 3))


@mcp.tool()
def detailsByDesignation(designation: str):
    """
    Give contact details of people working at IIT Mandi (professors and staff) based on their designation.
    It accepts partial or full designation titles (like 'Dean', 'Professor', 'Assistant Registrar', etc.)
    and returns the top fuzzy-matched contact details from the directory.
    """
    return contacts_dao.fuzzy_search_by_designation(designation, 0.6, 3)





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
     - Partial or full designation
     - Partial or full section
    And it will return the most relevant matches ranked by combined similarity.
    """

    return contacts_dao.fuzzy_search_by_designation_and_section(designation, section, 0.7, 5)



