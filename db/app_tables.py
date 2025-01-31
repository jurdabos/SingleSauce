def create_app_tables(conn, db_type="mysql"):
    """
    Creates the core application tables for the Single Sauce of Truth.
    This function handles both MySQL and SQLite schemas, including references
    and foreign keys, based on the db_type parameter.
    """
    cursor = conn.cursor()

    # For MySQL: ensure correct database selected
    if db_type == "mysql":
        cursor.execute("CREATE DATABASE IF NOT EXISTS singlesauce")
        cursor.execute("USE singlesauce")
    # For SQLite: enable foreign key enforcement
    elif db_type == "sqlite":
        cursor.execute("PRAGMA foreign_keys = ON")

    # Define statements for MySQL
    mysql_statements = [
        # Role table
        """
        CREATE TABLE IF NOT EXISTS role (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(255) NOT NULL UNIQUE
        )
        """,

        # User table
        """
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES role(id)
        )
        """,

        # Category table
        """
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            parent_category_id INT,
            FOREIGN KEY (parent_category_id) REFERENCES category(id)
        )
        """,

        # Recipe table
        """
        CREATE TABLE IF NOT EXISTS recipe (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            name_es VARCHAR(255),
            instructions TEXT NOT NULL,
            cooking_time_minutes INT,
            difficulty ENUM('beginner', 'intermediate', 'advanced'),
            source VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category_id INT,
            user_id INT,
            recipe_story_id INT,
            FOREIGN KEY (category_id) REFERENCES category(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
        """,

        # Ingredient table
        """
        CREATE TABLE IF NOT EXISTS ingredient (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            flavor_profile_id INT,
            health_data_id INT
        )
        """,

        # Recipe-Ingredient linking table
        """
        CREATE TABLE IF NOT EXISTS recipe_ingredient (
            recipe_id INT,
            ingredient_id INT,
            quantity VARCHAR(255),
            unit VARCHAR(255),
            optional BOOLEAN,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id),
            PRIMARY KEY (recipe_id, ingredient_id)
        )
        """,

        # Cohort table
        """
        CREATE TABLE IF NOT EXISTS cohort (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """,

        # User-Cohort linking
        """
        CREATE TABLE IF NOT EXISTS user_cohort (
            user_id INT,
            cohort_id INT,
            role ENUM('admin', 'member'),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (cohort_id) REFERENCES cohort(id),
            PRIMARY KEY (user_id, cohort_id)
        )
        """,

        # Cohort-Recipe linking
        """
        CREATE TABLE IF NOT EXISTS cohort_recipe (
            cohort_id INT,
            recipe_id INT,
            FOREIGN KEY (cohort_id) REFERENCES cohort(id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            PRIMARY KEY (cohort_id, recipe_id)
        )
        """,

        # Review table
        """
        CREATE TABLE IF NOT EXISTS review (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT,
          recipe_id INT,
          rating INT,
          comment TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES user(id),
          FOREIGN KEY (recipe_id) REFERENCES recipe(id)
        )
        """,

        # Photo table
        """
        CREATE TABLE IF NOT EXISTS photo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file MEDIUMBLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # Recipe-Photo linking
        """
        CREATE TABLE IF NOT EXISTS recipe_photo (
            recipe_id INT,
            photo_id INT,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (photo_id) REFERENCES photo(id),
            PRIMARY KEY (recipe_id, photo_id)
        )
        """,

        # Video table
        """
        CREATE TABLE IF NOT EXISTS video (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file MEDIUMBLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        # Recipe-Video linking
        """
        CREATE TABLE IF NOT EXISTS recipe_video (
            recipe_id INT,
            video_id INT,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (video_id) REFERENCES video(id),
            PRIMARY KEY (recipe_id, video_id)
        )
        """,
    ]

    # Define statements for SQLite
    sqlite_statements = [
        # Role table
        """
        CREATE TABLE IF NOT EXISTS role (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE
        );
        """,

        # User table
        """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES role(id)
        );
        """,

        # Category table
        """
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_category_id INTEGER,
            FOREIGN KEY (parent_category_id) REFERENCES category(id)
        );
        """,

        # Recipe table
        """
        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_es TEXT,
            instructions TEXT NOT NULL,
            cooking_time_minutes INTEGER,
            difficulty TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category_id INTEGER,
            user_id INTEGER,
            recipe_story_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES category(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
        """,

        # Ingredient table
        """
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            flavor_profile_id INTEGER,
            health_data_id INTEGER
        );
        """,

        # Recipe-Ingredient linking table
        """
        CREATE TABLE IF NOT EXISTS recipe_ingredient (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            quantity TEXT,
            unit TEXT,
            optional BOOLEAN,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id),
            PRIMARY KEY (recipe_id, ingredient_id)
        );
        """,

        # Cohort table
        """
        CREATE TABLE IF NOT EXISTS cohort (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """,

        # User-cohort linking
        """
        CREATE TABLE IF NOT EXISTS user_cohort (
            user_id INTEGER,
            cohort_id INTEGER,
            role TEXT,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (cohort_id) REFERENCES cohort(id),
            PRIMARY KEY (user_id, cohort_id)
        );
        """,

        # Cohort-recipe linking
        """
        CREATE TABLE IF NOT EXISTS cohort_recipe (
            cohort_id INTEGER,
            recipe_id INTEGER,
            FOREIGN KEY (cohort_id) REFERENCES cohort(id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            PRIMARY KEY (cohort_id, recipe_id)
        );
        """,

        # Review table
        """
        CREATE TABLE IF NOT EXISTS review (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          recipe_id INTEGER,
          rating INTEGER,
          comment TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES user(id),
          FOREIGN KEY (recipe_id) REFERENCES recipe(id)
        );
        """,

        # Photo table
        """
        CREATE TABLE IF NOT EXISTS photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # Recipe-photo linking
        """
        CREATE TABLE IF NOT EXISTS recipe_photo (
            recipe_id INTEGER,
            photo_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (photo_id) REFERENCES photo(id),
            PRIMARY KEY (recipe_id, photo_id)
        );
        """,

        # Video table
        """
        CREATE TABLE IF NOT EXISTS video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # Recipe-video linking
        """
        CREATE TABLE IF NOT EXISTS recipe_video (
            recipe_id INTEGER,
            video_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (video_id) REFERENCES video(id),
            PRIMARY KEY (recipe_id, video_id)
        );
        """,
    ]

    # Execute the statements in order
    if db_type == "mysql":
        for statement in mysql_statements:
            cursor.execute(statement.strip())
    else:
        for statement in sqlite_statements:
            cursor.execute(statement.strip())

    conn.commit()
    cursor.close()
    print("Application tables created successfully.")
