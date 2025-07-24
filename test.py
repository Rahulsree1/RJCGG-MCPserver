from db import contacts_dao

# contacts_dao.create_normalized_contact_directory_tables()
# contacts_dao.insert_normalized_directory_csv("./contacts.csv")

# contacts_dao.create_view_table()
data = contacts_dao.fuzzy_search_by_designation("dean students",threshold=0.7,limit=3)


print(data)