import psycopg2
import json

from sshtunnel import SSHTunnelForwarder

def get_login():
    with open("login.json") as f:
        credentials = json.loads(f.read())

        print(credentials)
        return (credentials['username'], credentials['password'])
    
def connect_to_db():
    username, password = get_login()
    with SSHTunnelForwarder(
            ('starbug.cs.rit.edu', 22),  # port 22 as standard SSH port
            ssh_username=username,
            ssh_password=password,
            remote_bind_address=('127.0.0.1', 5432)) as server:  # mirroring to local port 5432

        server.start()

        params = {  # database params
            'database': 'p320_18',
            'user': username,
            'password': password,
            'host': '127.0.0.1',
            'port': server.local_bind_port
        }
        conn = psycopg2.connect(**params)
        
        cur = conn.cursor()  # if this works, you are connected
        print("DB connected")

        # cur.execute("Select * from \"genre\"")
        # records = cur.fetchall()
        # for record in records:
        #     print(record)

def main():
    connect_to_db()
    

if __name__ == '__main__':
    main()
