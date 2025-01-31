import logging.config
import mysql.connector
import os
import pandas as pd
import yaml

# Kivy imports
import kivy

kivy.require("2.1.0")  # or whatever version
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from db.db import db_configuration

###############################################
# LOGGING SETUP
###############################################
try:
    with open("logging.yaml", "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
except FileNotFoundError:
    logging.basicConfig(level=logging.DEBUG)
    logging.warning("logging.yaml not found, using basicConfig at DEBUG level.")

logger = logging.getLogger("app")


###############################################
# RECIPE APP CLASS
###############################################
class RecipeApp:
    """
    Handles database logic, ETL operations, etc.
    Also can handle 'ingredient' if needed.
    """

    def __init__(self, db_config):
        self.db_config = db_config
        self.logger = logging.getLogger("app")
        self.logger.debug("Initializing RecipeApp with given DB config.")
        self.initialize_database()

    def initialize_database(self):
        self.logger.info("Checking/initializing the database schema...")
        # Example: We can call db/app_tables.py or rely on scripts/setup_db.py here
        self.logger.info("Database is ready or already set up.")

    ######################
    # ETL-Related Methods
    ######################
    def run_etl_flow(self, source_path, load_type="historic"):
        self.logger.info(f"Running {load_type} ETL flow with source: {source_path}")
        data = self.extract_data(source_path)
        if data is not None:
            transformed_data = self.transform_data(data)
            self.load_data(transformed_data, load_type)
        else:
            self.logger.error(f"Failed to extract data from {source_path}")

    def extract_data(self, source_path):
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
        self.logger.debug("Transforming data...")
        transformed_data = data.copy()

        rename_map = {
            "recipe_name": "name",
            "ingredients_list": "instructions",
            "prep_time": "cooking_time_minutes",
        }
        transformed_data.rename(columns=rename_map, inplace=True)

        if "name" in transformed_data.columns:
            old_count = len(transformed_data)
            transformed_data.drop_duplicates(subset=["name"], inplace=True)
            new_count = len(transformed_data)
            self.logger.debug(f"Removed {old_count - new_count} duplicates by 'name'.")
        self.logger.info("Data transformation complete.")
        return transformed_data

    def load_data(self, data: pd.DataFrame, load_type: str):
        self.logger.info(f"Loading data into the 'recipe' table for {load_type} flow.")
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            # Inserting only a subset of columns for demonstration
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

    ######################
    # RECIPE CRUD Methods
    ######################
    def list_recipes(self, limit=50):
        rows = []
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, name_es, instructions, cooking_time_minutes,
                       difficulty, source, category_id, user_id, recipe_story_id
                FROM recipe
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.logger.exception(f"Error fetching recipes: {err}")
        return rows

    def add_recipe(self, name, instructions, cooking_time=None, difficulty=None,
                   source=None, name_es=None, category_id=None, user_id=None,
                   recipe_story_id=None):
        """
        Insert a new record into the 'recipe' table, respecting its columns:
          name, name_es, instructions, cooking_time_minutes, difficulty, source,
          category_id, user_id, recipe_story_id
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO recipe
                (name, name_es, instructions, cooking_time_minutes,
                 difficulty, source, category_id, user_id, recipe_story_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                name, name_es, instructions, cooking_time, difficulty, source,
                category_id, user_id, recipe_story_id
            ))
            conn.commit()
            cursor.close()
            conn.close()
            self.logger.info(f"Inserted new recipe: {name}")
        except mysql.connector.Error as err:
            self.logger.exception(f"Error inserting new recipe: {err}")

    def list_categories(self):
        """
        Returns a list of categories, each as a dict:
        [{'id': 1, 'name': 'Main Dishes'}, ...]
        """
        rows = []
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM category")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.logger.exception(f"Error fetching categories: {err}")
        return rows

    ######################
    # INGREDIENT Methods
    ######################
    def list_ingredients(self, limit=50):
        rows = []
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, description, flavor_profile_id, health_data_id
                FROM ingredient
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.logger.exception(f"Error fetching ingredients: {err}")
        return rows

    def add_ingredient(self, name, description=None, flavor_profile_id=None, health_data_id=None):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO ingredient (name, description, flavor_profile_id, health_data_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, description, flavor_profile_id, health_data_id))
            conn.commit()
            cursor.close()
            conn.close()
            self.logger.info(f"Inserted new ingredient: {name}")
        except mysql.connector.Error as err:
            self.logger.exception(f"Error inserting new ingredient: {err}")


###############################################
# KIVY UI: SCREENS & APP
###############################################

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="Single Sauce of Truth (Kivy)", font_size=24))
        btn_list = Button(text="List Recipes")
        btn_add = Button(text="Add Recipe")
        btn_etl = Button(text="Run ETL Flow (Example)")
        btn_list.bind(on_press=self.goto_list_recipes)
        btn_add.bind(on_press=self.goto_add_recipe)
        btn_etl.bind(on_press=self.run_etl_flow)
        layout.add_widget(btn_list)
        layout.add_widget(btn_add)
        layout.add_widget(btn_etl)
        self.add_widget(layout)

    def goto_list_recipes(self, instance):
        self.manager.current = "list_recipes"

    def goto_add_recipe(self, instance):
        self.manager.current = "add_recipe"

    def run_etl_flow(self, instance):
        # Instead of app.root_app, use App.get_running_app().recipe_app
        current_app = App.get_running_app()
        current_app.recipe_app.run_etl_flow("data/historic_recipes.csv", "historic")


class ListRecipesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        title = Label(text="Recipe List", font_size=20)
        self.layout.add_widget(title)
        self.result_layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
        self.layout.add_widget(self.result_layout)
        btn_back = Button(text="Back to Main Menu", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.goto_main_menu)
        self.layout.add_widget(btn_back)
        self.add_widget(self.layout)

    def on_enter(self):
        # Called whenever we navigate to this screen
        self.refresh_recipes()

    def refresh_recipes(self):
        self.result_layout.clear_widgets()
        current_app = App.get_running_app()
        recipes = current_app.recipe_app.list_recipes(limit=50)
        for r in recipes:
            # Display more columns, e.g. name_es, difficulty, source
            line = (f"ID: {r['id']} | {r['name']} (ES: {r.get('name_es', '-')}) | "
                    f"{r['instructions']} | {r.get('difficulty', '?')} | "
                    f"{r.get('source', '?')} | {r.get('cooking_time_minutes', '?')} mins")
            self.result_layout.add_widget(Label(text=line, font_size=14))

    def goto_main_menu(self, instance):
        self.manager.current = "main_menu"


class AddRecipeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.layout.add_widget(Label(text="Add a New Recipe", font_size=20))
        # Name field
        self.name_input = TextInput(hint_text="Name", multiline=False)
        self.layout.add_widget(self.name_input)
        # Spanish name field
        self.name_es_input = TextInput(hint_text="Name (Spanish)", multiline=False)
        self.layout.add_widget(self.name_es_input)
        # Instructions field
        self.instructions_input = TextInput(hint_text="Instructions", multiline=True, size_hint_y=None, height=100)
        self.layout.add_widget(self.instructions_input)
        # Cooking time
        self.cooking_time_input = TextInput(hint_text="Cooking Time (minutes)", multiline=False)
        self.layout.add_widget(self.cooking_time_input)
        # Difficulty
        self.difficulty_input = TextInput(hint_text="Difficulty (beginner/intermediate/advanced)", multiline=False)
        self.layout.add_widget(self.difficulty_input)
        # Source
        self.source_input = TextInput(hint_text="Source (URL or reference)", multiline=False)
        self.layout.add_widget(self.source_input)

        # 1. Fetch categories from the DB
        current_app = App.get_running_app()
        category_rows = current_app.recipe_app.list_categories()  # returns [{'id':1,'name':'Main Dishes'}, ...]
        # 2. Create a mapping: category_name -> category_id
        self.category_map = {cat['name']: cat['id'] for cat in category_rows}
        # 3. Spinner with category names
        if category_rows:
            # Use the first category's name as default, or "Select Category"
            default_text = "Select Category"
            cat_names = list(self.category_map.keys())
        else:
            default_text = "No categories found"
            cat_names = []
        self.category_spinner = Spinner(
            text=default_text,
            values=cat_names,
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(self.category_spinner)

        # User ID
        self.user_id_input = TextInput(hint_text="User ID (int)", multiline=False)
        self.layout.add_widget(self.user_id_input)
        # Recipe Story ID
        self.recipe_story_id_input = TextInput(hint_text="Recipe Story ID (int)", multiline=False)
        self.layout.add_widget(self.recipe_story_id_input)
        # Save Button
        btn_save = Button(text="Save Recipe")
        btn_save.bind(on_press=self.save_recipe)
        self.layout.add_widget(btn_save)
        # Back Button
        btn_back = Button(text="Back to Main Menu")
        btn_back.bind(on_press=self.goto_main_menu)
        self.layout.add_widget(btn_back)
        self.add_widget(self.layout)

    def save_recipe(self, instance):
        current_app = App.get_running_app()
        # Gather field data
        name = self.name_input.text.strip()
        name_es = self.name_es_input.text.strip()
        instructions = self.instructions_input.text.strip()
        cooking_time = self.cooking_time_input.text.strip()
        difficulty = self.difficulty_input.text.strip()
        source = self.source_input.text.strip()

        selected_category_name = self.category_spinner.text
        category_id = self.category_map.get(selected_category_name, None)

        user_id = self.user_id_input.text.strip()
        recipe_story_id = self.recipe_story_id_input.text.strip()
        # Convert numeric fields
        cooking_time_int = int(cooking_time) if cooking_time.isdigit() else None
        category_id_int = int(category_id) if category_id.isdigit() else None
        user_id_int = int(user_id) if user_id.isdigit() else None
        recipe_story_id_int = int(recipe_story_id) if recipe_story_id.isdigit() else None
        # Insert into DB
        current_app.recipe_app.add_recipe(
            name=name,
            name_es=name_es,
            instructions=instructions,
            cooking_time=cooking_time_int,
            difficulty=difficulty,
            source=source,
            category_id=category_id,
            user_id=user_id,
            recipe_story_id=recipe_story_id
        )
        # Clear fields
        self.name_input.text = ""
        self.name_es_input.text = ""
        self.instructions_input.text = ""
        self.cooking_time_input.text = ""
        self.difficulty_input.text = ""
        self.source_input.text = ""
        self.category_id_input.text = ""
        self.user_id_input.text = ""
        self.recipe_story_id_input.text = ""
        self.category_spinner.text = "Select Category"
        self.manager.current = "main_menu"

    def goto_main_menu(self, instance):
        self.manager.current = "main_menu"


class MainScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_menu_screen = MainMenuScreen(name="main_menu")
        self.list_recipes_screen = ListRecipesScreen(name="list_recipes")
        self.add_recipe_screen = AddRecipeScreen(name="add_recipe")
        self.add_widget(self.main_menu_screen)
        self.add_widget(self.list_recipes_screen)
        self.add_widget(self.add_recipe_screen)


class SingleSauceKivyApp(App):
    """
    Our main Kivy application.
    We'll hold a reference to 'RecipeApp' so we can call its methods from screens.
    """

    def __init__(self, recipe_app, **kwargs):
        super().__init__(**kwargs)
        self.recipe_app = recipe_app

    def build(self):
        sm = MainScreenManager()
        return sm


if __name__ == "__main__":
    logger.info("Starting Single Sauce of Truth with Kivy UI...")
    # Initializing the database logic
    root_recipe_app = RecipeApp(db_configuration)
    # Initializing Kivy App with the RecipeApp object
    app = SingleSauceKivyApp(recipe_app=root_recipe_app)
    app.run()
