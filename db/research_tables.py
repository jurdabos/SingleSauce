import mysql.connector
from db.get_connection import get_db_connection


def create_research_tables(db_config):
    """Creates the database and necessary tables."""
    try:
        conn = get_db_connection("mysql", db_config)
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS singlesauce")
        cursor.execute("USE singlesauce")

        # Create the two tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_sources_general (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255),
            weighted_average FLOAT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_sources_percentage (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255),
            percentage VARCHAR(255)
        )
        """)

        print("Database and tables created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.commit()
        cursor.close()
        conn.close()