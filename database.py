import psycopg2

from sshtunnel import SSHTunnelForwarder

class Database:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


    def query(self, query: str):
        try:
            with SSHTunnelForwarder(
                    ('starbug.cs.rit.edu', 22),  # port 22 as standard SSH port
                    ssh_username=self.username,
                    ssh_password=self.password,
                    remote_bind_address=('127.0.0.1', 5432)) as server:  # mirroring to local port 5432

                server.start()

                params = {  # database params
                    'database': 'p320_18',
                    'user': self.username,
                    'password': self.password,
                    'host': '127.0.0.1',
                    'port': server.local_bind_port
                }
                conn = psycopg2.connect(**params)
                cur = conn.cursor()  # if this works, you are connected
                cur.execute(query)
                return cur.fetchall()
        except:
            print("Error connecting to DB")
