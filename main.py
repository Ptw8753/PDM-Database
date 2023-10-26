from json import loads
from interface import Interface


def get_login():
    with open("login.json") as f:
        credentials = loads(f.read())

        return (credentials['username'], credentials['password'])


def main():
    username, password = get_login()
    interface = Interface(username, password)
    print(interface.getSongByMinTimePlayed("200"))


if __name__ == '__main__':
    main()