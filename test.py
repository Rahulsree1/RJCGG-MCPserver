# from db import contacts_dao, mess_dao

# contacts_dao.create_normalized_contact_directory_tables()
# contacts_dao.insert_normalized_directory_csv("./contacts.csv")

# contacts_dao.create_view_table()


# mess_dao.create_mess_menu_table()
# mess_dao.insert_menu_from_json("./mess_menu.json")

# data = contacts_dao.fuzzy_search_by_designation("dean students",threshold=0.7,limit=3)

# data = mess_dao.get_items_by_day_and_meal('monday', 'lunch')

# print(data)


temp =', '.join([ i+ "@studnets" for i in "dfssd".split(',')])
print(temp)