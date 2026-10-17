import os

import mysql.connector

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_connection():

    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "vehicle_app"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "vehicle_rental"),
        )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None


def run_query(sql, params=(), fetch=False):

    connection = get_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        connection.close()
