# test_postgres.py
import os
import psycopg2
from psycopg2 import OperationalError

# Paramètres de connexion
DB_HOST = "localhost"
DB_NAME = os.getenv("POSTGRES_DB", "odoo")
DB_USER = os.getenv("POSTGRES_USER", "odoo")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "odoo")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)

def test_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        print("Connexion PostgreSQL réussie !")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("Version PostgreSQL :", version)
        cur.close()
        conn.close()
    except OperationalError as e:
        print("Erreur de connexion PostgreSQL :", e)

if __name__ == "__main__":
    test_connection()
