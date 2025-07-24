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
def detailsByDesignation(designation: str):
    """
    Give contact details of people working at IIT Mandi (professors and staff) based on their designation.
    It accepts partial or full designation titles (like 'Dean students', 'Professor', 'Assistant Registrar', etc.)
    and returns the top fuzzy-matched contact details from the directory.
    """
    return contacts_dao.fuzzy_search_by_designation(designation, 0.7, 5)


