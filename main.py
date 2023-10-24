import os

from DB import *

database = Database(os.environ.get("Username"), os.environ.get("Password"))

print(database.query("SELECT * FROM \"Genre\""))