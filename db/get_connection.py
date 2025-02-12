import os
import mysql.connector
import sqlite3


def get_db_connection(db_type, db_config):
    """
    Returns a database connection object based on db_type.
    """
    if db_type == "mysql":
        return mysql.connector.connect(**db_config)
    elif db_type == "sqlite":
        db_path = os.environ.get("LOCAL_DB_PATH", "local_recipes.sqlite")
        conn = sqlite3.connect(db_path)
        # Enabling foreign key constraints:
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")
