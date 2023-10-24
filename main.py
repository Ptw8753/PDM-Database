import json
from DB import Database

from sshtunnel import SSHTunnelForwarder


def get_login():
    with open("login.json") as f:
        credentials = json.loads(f.read())

        return (credentials['username'], credentials['password'])


def main():
    login = get_login()
    database = Database(login[0], login[1])
    print(database.query("Select * from \"genre\""))

if __name__ == '__main__':
    main()