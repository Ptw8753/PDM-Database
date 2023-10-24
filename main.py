import os
import psycopg2

from sshtunnel import SSHTunnelForwarder

with SSHTunnelForwarder(
        ('starbug.cs.rit.edu', 22),  # port 22 as standard SSH port
        ssh_username=os.environ.get("Username"),
        ssh_password=os.environ.get("Password"),
        remote_bind_address=('127.0.0.1', 5432)) as server:  # mirroring to local port 5432

    server.start()

    params = {  # database params
        'database': 'p320_18',
        'user': os.environ.get("Username"),
        'password': os.environ.get("Password"),
        'host': '127.0.0.1',
        'port': server.local_bind_port
    }
    conn = psycopg2.connect(**params)
    cur = conn.cursor()  # if this works, you are connected
    print("DB connected")
    cur.execute("Select * from \"Genre\"")
    records = cur.fetchall()
    for record in records:
        print(record)


