from db import mess_dao
import json

# mess_dao.create_mess_table()


f = json.loads(open("./mess_menu.json").read())

days = f.keys()


# for i in days:
#     meal_types = f[i]
#     for j in meal_types:
#         items = f[i][j]
#         mess_dao.add_menu_row(i,j,items)

mess_dao.add_single_item_to_menu("Monday", "Dinner", "Roti")
