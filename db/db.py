import os
import mysql.connector
import pandas as pd

# Configuration for MySQL
db_configuration = {
    "host": os.environ.get("MyDB_HOST", "localhost"),
    "user": os.environ.get("MyDB_USER", "singleuser"),  # default user
    "password": os.environ.get("MyDB_PASSWORD", "singlepass"),  # default pass
    "database": "singlesauce",
    "use_pure": True
}


def bulk_insert_recipes_with_ingredients(conn, recipes_df, db_type="mysql", batch_size=1000):
    """
    Bulk insert to handle large volumes of recipe data AND their ingredient references.
    Expecting 'recipes_df' to have columns at least for:
      - name, instructions, cooking_time_minutes, etc. (for recipe)
      - some representation of ingredients (e.g. 'ingredients_info'), which might be
        a list of dicts or a string we can parse.
    We'll:
      1) Insert the 'recipe' row
      2) Retrieve the newly generated recipe.id
      3) Parse 'ingredients_info' to insert bridging rows into 'recipe_ingredient'
    """
    recipe_insert_sql_mysql = """
        INSERT INTO recipe (
            name, instructions, cooking_time_minutes
        )
        VALUES (%s, %s, %s)
    """
    recipe_insert_sql_sqlite = """
        INSERT INTO recipe (
            name, instructions, cooking_time_minutes
        )
        VALUES (?, ?, ?)
    """
    # For bridging table
    recipe_ingredient_insert_sql_mysql = """
        INSERT INTO recipe_ingredient (
            recipe_id, ingredient_id,
            quantity, unit, optional
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    recipe_ingredient_insert_sql_sqlite = """
        INSERT INTO recipe_ingredient (
            recipe_id, ingredient_id,
            quantity, unit, optional
        )
        VALUES (?, ?, ?, ?, ?)
    """
    # Deciding which queries to use depending on db_type
    if db_type == "mysql":
        recipe_insert_sql = recipe_insert_sql_mysql
        recipe_ingredient_insert_sql = recipe_ingredient_insert_sql_mysql
    else:
        recipe_insert_sql = recipe_insert_sql_sqlite
        recipe_ingredient_insert_sql = recipe_ingredient_insert_sql_sqlite
    cursor = conn.cursor()
    recipe_data_buffer = []
    bridging_data_buffer = []
    count = 0
    for _, row in recipes_df.iterrows():
        recipe_name = row.get("name", "")
        recipe_instructions = row.get("instructions", "")
        recipe_time = row.get("cooking_time_minutes", None)
        # 1) Inserting the recipe
        cursor.execute(recipe_insert_sql, (recipe_name, recipe_instructions, recipe_time))
        conn.commit()  # Committing so we can retrieve the new primary key
        # 2) Retrieving the newly generated recipe.id
        new_recipe_id = cursor.lastrowid
        # 3) Suppose the row has 'ingredients_info' describing the bridging data
        # e.g. a list of dicts or a string. We'll do a minimal example:
        ingredients_info = row.get("ingredients_info", "")
        # If it's a string like "ingredient_id=3,quantity=2 tbsp; ingredient_id=7,quantity=100 g"
        # we'd parse it. Or if it's a Python list (when read from JSON), we will handle that logic here.
        # PLACEHOLDER for handling Python-list logic here
        # Let's assume it's a list of dicts for demonstration:
        # e.g. row["ingredients_info"] = [
        #   {"ingredient_id":3, "quantity":"2", "unit":"tbsp", "optional":False},
        #   {"ingredient_id":7, "quantity":"100", "unit":"g", "optional":True}
        # ]
        if isinstance(ingredients_info, list):
            for ing in ingredients_info:
                ingredient_id = ing.get("ingredient_id")
                quantity = ing.get("quantity", "")
                unit = ing.get("unit", "")
                optional = ing.get("optional", False)
                bridging_data_buffer.append((
                    new_recipe_id,
                    ingredient_id,
                    quantity,
                    unit,
                    optional
                ))
        # If bridging_data_buffer grows large, flush it
        if len(bridging_data_buffer) >= batch_size:
            cursor.executemany(recipe_ingredient_insert_sql, bridging_data_buffer)
            conn.commit()
            bridging_data_buffer = []
        count += 1
    # After loop ends, we flush any remaining bridging rows
    if bridging_data_buffer:
        cursor.executemany(recipe_ingredient_insert_sql, bridging_data_buffer)
        conn.commit()
    print(f"Bulk insert complete: {count} recipes inserted (plus bridging data).")
    cursor.close()


def fetch_recipes_with_ingredients(conn, limit=10):
    """
    Fetch recipes and their ingredient bridging info, returning a nested structure.
    Example return:
    [
      {
        'id': 1,
        'name': 'Pizza',
        'name_es': 'Pizza (ES)',
        'instructions': '...',
        'cooking_time_minutes': 10,
        'difficulty': 'beginner',
        'source': 'Family Recipe',
        'category_id': 1,
        'user_id': 2,
        'recipe_story_id': None,
        'ingredients': [
          {
            'ingredient_id': 3,
            'ingredient_name': 'Tomato',
            'quantity': '2',
            'unit': 'tbsp',
            'optional': False
          },
          ...
        ]
      },
      ...
    ]
    """
    cursor = conn.cursor(dictionary=True)
    # We'll do a 3-way LEFT JOIN because we want
    #  - all columns from recipe
    #  - bridging data from recipe_ingredient
    #  - ingredient name from ingredient
    query = """
        SELECT
            r.id AS recipe_id,
            r.name AS recipe_name,
            r.name_es,
            r.instructions,
            r.cooking_time_minutes,
            r.difficulty,
            r.source,
            r.created_at,
            r.category_id,
            r.user_id,
            r.recipe_story_id,
            ri.ingredient_id,
            ri.quantity,
            ri.unit,
            ri.optional,
            ing.name AS ingredient_name
        FROM recipe r
        LEFT JOIN recipe_ingredient ri ON r.id = ri.recipe_id
        LEFT JOIN ingredient ing ON ri.ingredient_id = ing.id
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    cursor.close()
    # We'll group the rows by recipe_id
    recipe_dict = {}
    for row in rows:
        rid = row["recipe_id"]
        if rid not in recipe_dict:
            # Create a new recipe entry in the grouping structure
            recipe_dict[rid] = {
                "id": rid,
                "name": row["recipe_name"],
                "name_es": row["name_es"],
                "instructions": row["instructions"],
                "cooking_time_minutes": row["cooking_time_minutes"],
                "difficulty": row["difficulty"],
                "source": row["source"],
                "created_at": row["created_at"],
                "category_id": row["category_id"],
                "user_id": row["user_id"],
                "recipe_story_id": row["recipe_story_id"],
                "ingredients": []
            }
        # If ingredient_id is None, it means no bridging row
        if row["ingredient_id"] is not None:
            recipe_dict[rid]["ingredients"].append({
                "ingredient_id": row["ingredient_id"],
                "ingredient_name": row["ingredient_name"],
                "quantity": row["quantity"],
                "unit": row["unit"],
                "optional": bool(row["optional"]) if row["optional"] is not None else False
            })
    # Converting the dict to a list
    recipe_list = list(recipe_dict.values())
    return recipe_list


def fetch_data_from_csv(csvpath):
    """
    Simple CSV loader using pandas.
    """
    if os.path.exists(csvpath):
        return pd.read_csv(csvpath)
    else:
        print(f"File {csvpath} not found.")
        return None
