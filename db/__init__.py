# db/__init__.py
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import pool
from pathlib import Path

# Load the .env file from utils/env/
env_path = Path(__file__).resolve().parent.parent / 'utils' / '.env'
load_dotenv(dotenv_path=env_path)



_postgres_pool = None

def init_db_pool():
    global _postgres_pool
    if _postgres_pool is None:
        _postgres_pool = psycopg2.pool.SimpleConnectionPool(
            1, 5,
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

def get_connection():
    if _postgres_pool is None:
        raise Exception("DB Pool not initialized. Call init_db_pool() first.")
    return _postgres_pool.getconn()

def return_connection(conn):
    if _postgres_pool:
        _postgres_pool.putconn(conn)

def close_all_connections():
    if _postgres_pool:
        _postgres_pool.closeall()


init_db_pool()