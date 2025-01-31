import os
import mysql.connector
import pandas as pd

# Configuration for MySQL connection
db_configuration = {
    "host": os.environ.get("MyDB_HOST", "localhost"),
    "user": os.environ.get("MyDB_USER", "singleuser"),  # default user
    "password": os.environ.get("MyDB_PASSWORD", "singlepass"), # default pass
    "database": "singlesauce",
    "use_pure": True
}


def bulk_insert_recipes(conn, recipes_df, db_type="mysql", batch_size=1000):
    """
    Bulk insert to handle large volumes of recipe data into the updated 'recipe' table.
    The schema for 'recipe' now includes:
      - id (AUTO_INCREMENT)
      - name (VARCHAR(255))
      - name_es (VARCHAR(255))
      - instructions (TEXT)
      - cooking_time_minutes (INT)
      - difficulty (ENUM(...) or TEXT in SQLite)
      - source (VARCHAR(255))
      - created_at (TIMESTAMP, defaults to CURRENT_TIMESTAMP)
      - category_id (INT)
      - user_id (INT)
      - recipe_story_id (INT)

    The example below maps columns from recipes_df to these DB columns.
    If our CSV lacks some columns (e.g., difficulty, category_id), we can omit them
    from both the INSERT statement and the data_buffer tuples.
    """

    cursor = conn.cursor()

    # If our data source, e. g. doesn't have some of them, we should remove them from the statement
    # (as well as from the data_buffer).
    if db_type == "mysql":
        insert_query = """
            INSERT INTO recipe (
                name, name_es, instructions,
                cooking_time_minutes, difficulty, source,
                category_id, user_id, recipe_story_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    else:  # sqlite
        insert_query = """
            INSERT INTO recipe (
                name, name_es, instructions,
                cooking_time_minutes, difficulty, source,
                category_id, user_id, recipe_story_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    data_buffer = []

    for _, row in recipes_df.iterrows():
        # Extracting columns from CSV DataFrame:
        recipe_name = row.get("name", "")
        recipe_name_es = row.get("name_es", "")
        recipe_instructions = row.get("instructions", "")
        recipe_time = row.get("cooking_time_minutes", None)
        recipe_difficulty = row.get("difficulty", None)
        recipe_source = row.get("source", "")
        recipe_category_id = row.get("category_id", None)
        recipe_user_id = row.get("user_id", None)
        recipe_story_id = row.get("recipe_story_id", None)

        # Append values in the same order as the INSERT statement
        data_buffer.append((
            recipe_name,
            recipe_name_es,
            recipe_instructions,
            recipe_time,
            recipe_difficulty,
            recipe_source,
            recipe_category_id,
            recipe_user_id,
            recipe_story_id
        ))

        # If buffer is full, commit the batch
        if len(data_buffer) >= batch_size:
            cursor.executemany(insert_query, data_buffer)
            conn.commit()
            data_buffer = []

    # Insert any remaining records
    if data_buffer:
        cursor.executemany(insert_query, data_buffer)
        conn.commit()

    print(f"Bulk insert complete: {len(recipes_df)} records inserted.")
    cursor.close()


def fetch_recipes(conn):
    """
    Example function to fetch some data from the 'recipe' table.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id, name, name_es, instructions, cooking_time_minutes,
            difficulty, source, category_id, user_id, recipe_story_id
        FROM recipe
        LIMIT 10
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def fetch_data_from_csv(csvpath):
    """
    Simple CSV loader using pandas.
    """
    if os.path.exists(csvpath):
        return pd.read_csv(csvpath)
    else:
        print(f"File {csvpath} not found.")
        return None
