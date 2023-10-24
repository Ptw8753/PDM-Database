import json
from Interface import Interface

from sshtunnel import SSHTunnelForwarder


def get_login():
    with open("login.json") as f:
        credentials = json.loads(f.read())

        return (credentials['username'], credentials['password'])


def main():
    login = get_login()
    interface = Interface(login[0], login[1])
    print(interface.getSongByMinTimePlayed("200"))

if __name__ == '__main__':
    main()