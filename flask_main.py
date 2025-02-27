import logging.config
import mysql.connector
import os
import pandas as pd
import yaml

from flask import Flask, request, redirect, url_for, render_template_string

########################
# IMPORT DB CONFIG & OPTIONAL TABLE CREATION
########################
from db.db import db_configuration

# from db.app_tables import create_app_tables  # optional if we want to auto-create the schema
# from db.get_connection import get_db_connection  # if we prefer a function-based approach

########################
# LOGGING SETUP
########################
try:
    with open("logging.yaml", "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
except FileNotFoundError:
    logging.basicConfig(level=logging.DEBUG)
    logging.warning("logging.yaml not found, using basicConfig at DEBUG level.")

logger = logging.getLogger("app")

########################
# FLASK APP SETUP
########################
app = Flask(__name__)


########################
# RECIPE APP CLASS
########################
class RecipeApp:
    """
    RecipeApp serves as the foundation for a centralized recipe management service.
    It handles ETL operations, database interactions, and user-facing API logic.
    """
    def __init__(self, db_config):
        self.db_config = db_config
        self.logger = logging.getLogger("app")
        self.logger.debug("Initializing RecipeApp with given DB config.")
        self.initialize_database()

    def initialize_database(self):
        """
        Ensures that the database and necessary tables exist.
        """
        self.logger.info("Checking/initializing the database schema...")
        # Optional code if we want to create tables automatically:
        # from db.app_tables import create_app_tables
        # conn = get_db_connection("mysql", self.db_config)
        # create_app_tables(conn, db_type="mysql")
        # conn.close()
        self.logger.info("Database is ready or already set up.")

    def run_etl_flow(self, source_path, load_type="historic"):
        """
        Executes an ETL flow to migrate recipes into the database.
        """
        self.logger.info(f"Running {load_type} ETL flow with source: {source_path}")
        data = self.extract_data(source_path)
        if data is not None:
            transformed_data = self.transform_data(data)
            self.load_data(transformed_data, load_type)
        else:
            self.logger.error(f"Failed to extract data from {source_path}")

    def extract_data(self, source_path):
        """
        Extracts data from a given source file (CSV or JSON).
        """
        self.logger.debug(f"Extracting data from {source_path}...")
        if not os.path.exists(source_path):
            self.logger.error(f"File not found: {source_path}")
            return None
        file_ext = os.path.splitext(source_path)[1].lower()
        try:
            if file_ext == ".csv":
                df = pd.read_csv(source_path)
            elif file_ext == ".json":
                df = pd.read_json(source_path)
            else:
                self.logger.warning("Unsupported file format. Please use CSV or JSON.")
                return None
        except Exception as e:
            self.logger.exception(f"Exception while reading file: {e}")
            return None
        self.logger.info(f"Extracted {len(df)} rows of data from {source_path}")
        return df

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms extracted data to fit the centralized recipe repository schema.
        """
        self.logger.debug("Transforming data...")
        transformed_data = data.copy()
        # Example rename
        rename_map = {
            "recipe_name": "name",
            "ingredients_list": "instructions",  # or "ingredients"
            "prep_time": "cooking_time_minutes",
        }
        transformed_data.rename(columns=rename_map, inplace=True)

        # Example dedup
        if "name" in transformed_data.columns:
            old_count = len(transformed_data)
            transformed_data.drop_duplicates(subset=["name"], inplace=True)
            new_count = len(transformed_data)
            self.logger.debug(f"Removed {old_count - new_count} duplicates by 'name'.")

        self.logger.info("Data transformation complete.")
        return transformed_data

    def load_data(self, data: pd.DataFrame, load_type: str):
        """
        Loads transformed data into the 'recipe' table.
        """
        self.logger.info(f"Loading data into the 'recipe' table for {load_type} flow.")
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO recipe (name, instructions, cooking_time_minutes)
                VALUES (%s, %s, %s)
            """
            count = 0
            for _, row in data.iterrows():
                name = row.get("name", "")
                instructions = row.get("instructions", "")
                cooking_time = row.get("cooking_time_minutes", None)
                cursor.execute(insert_sql, (name, instructions, cooking_time))
                count += 1
            conn.commit()
            self.logger.info(f"{load_type.capitalize()} load complete. Inserted {count} rows.")
        except mysql.connector.Error as err:
            self.logger.exception(f"Error during data loading: {err}")
        finally:
            cursor.close()
            conn.close()


########################
# INSTANTIATE THE RECIPE APP
########################
recipe_app = RecipeApp(db_configuration)


########################
# FLASK ROUTES
########################

@app.route("/")
def main_menu():
    """
    Displays a simple menu to the user. This acts like a 'home page.'
    """
    return render_template_string("""
    <h1>Single Sauce of Truth</h1>
    <ul>
      <li><a href="{{ url_for('list_recipes') }}">List Recipes</a></li>
      <li><a href="{{ url_for('add_recipe') }}">Add a New Recipe</a></li>
      <li><a href="{{ url_for('run_etl') }}">Run ETL Flow (Example)</a></li>
    </ul>
    """)


@app.route("/recipes")
def list_recipes():
    """
    Shows a simple list of recipes from the 'recipe' table.
    """
    logger.debug("User requested to list recipes.")
    try:
        conn = mysql.connector.connect(**db_configuration)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, instructions, cooking_time_minutes FROM recipe LIMIT 50")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logger.exception(f"Error fetching recipes: {err}")
        rows = []

    # Basic HTML rendering
    html = """
    <h2>Recipe List (showing up to 50)</h2>
    <a href="/">Back to Main Menu</a>
    <table border="1">
      <tr><th>ID</th><th>Name</th><th>Instructions</th><th>Cooking Time (min)</th></tr>
      {% for row in rows %}
      <tr>
        <td>{{ row.id }}</td>
        <td>{{ row.name }}</td>
        <td>{{ row.instructions }}</td>
        <td>{{ row.cooking_time_minutes }}</td>
      </tr>
      {% endfor %}
    </table>
    """
    return render_template_string(html, rows=rows)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    """
    GET: Display a form for creating a new recipe.
    POST: Insert the new recipe into the database and redirect.
    """
    if request.method == "POST":
        name = request.form.get("name", "")
        instructions = request.form.get("instructions", "")
        cooking_time = request.form.get("cooking_time_minutes", "")
        difficulty = request.form.get("difficulty", "")
        source = request.form.get("source", "")

        # For demonstration, ignoring category_id, user_id, etc.
        # We can add them to the form later when we have time and store them similarly.

        try:
            conn = mysql.connector.connect(**db_configuration)
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO recipe (name, instructions, cooking_time_minutes, difficulty, source)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Convert cooking_time to int if provided
            cooking_time_int = int(cooking_time) if cooking_time.isdigit() else None
            cursor.execute(insert_sql, (name, instructions, cooking_time_int, difficulty, source))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Inserted new recipe: {name}")
        except mysql.connector.Error as err:
            logger.exception(f"Error inserting new recipe: {err}")

        return redirect(url_for("list_recipes"))
    else:
        # GET request: display form
        html_form = """
        <h2>Add a New Recipe</h2>
        <a href="/">Back to Main Menu</a>
        <form method="POST">
          <label>Name:</label><br>
          <input type="text" name="name" required><br><br>

          <label>Instructions:</label><br>
          <textarea name="instructions" rows="4" cols="50"></textarea><br><br>

          <label>Cooking Time (minutes):</label><br>
          <input type="text" name="cooking_time_minutes"><br><br>

          <label>Difficulty (beginner/intermediate/advanced):</label><br>
          <select name="difficulty">
            <option value="">--None--</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select><br><br>

          <label>Source:</label><br>
          <input type="text" name="source"><br><br>

          <!-- Additional fields: category_id, user_id, etc. if needed -->

          <button type="submit">Save Recipe</button>
        </form>
        """
        return render_template_string(html_form)


@app.route("/run_etl")
def run_etl():
    """
    Example route that triggers the ETL flow on a given file.
    """
    # For the sake of demo, let's use a static path or you could pass it as a query param
    source_path = "data/historic_recipes.csv"
    recipe_app.run_etl_flow(source_path, load_type="historic")
    return """
    <h3>ETL flow triggered.</h3>
    <a href="/">Back to Main Menu</a>
    """


########################
# MAIN EXECUTION
########################
if __name__ == "__main__":
    logger.info("Starting the Single Sauce of Truth Flask app...")

    # Example: If you want to do an ETL run at startup, do it here:
    # recipe_app.run_etl_flow("data/historic_recipes.csv", "historic")

    # Start the Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)
