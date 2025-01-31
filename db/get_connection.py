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
        # If LOCAL_DB_PATH variable is set, `db_path` is assigned its value.
        # If not, `db_path` defaults to "local_recipes.sqlite".
        return sqlite3.connect(db_path)
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")
