import psycopg2

from sshtunnel import SSHTunnelForwarder

class Database:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        try:
            self.server = SSHTunnelForwarder(
                ('starbug.cs.rit.edu', 22),  # port 22 as standard SSH port
                ssh_username=self.username,
                ssh_password=self.password,
                remote_bind_address=('127.0.0.1', 5432))
            self.server.start()

            params = {  # database params
                'database': 'p320_18',
                'user': self.username,
                'password': self.password,
                'host': '127.0.0.1',
                'port': self.server.local_bind_port
            }
            conn = psycopg2.connect(**params)
            conn.autocommit = True
            self.cur = conn.cursor()  # if this works, you are connected
        except:
            print("error connecting to DB")

    def disconnect(self):
        self.server.stop()

    def query(self, query: str):
        self.cur.execute(query)
        try:
            
            result = self.cur.fetchall()
        except:
            return None
        return result
