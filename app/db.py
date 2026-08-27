import os
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def get_connection():
    return connection_pool.getconn()

def put_connection(conn):
    connection_pool.putconn(conn)