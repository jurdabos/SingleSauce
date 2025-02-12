Single Sauce of Truth: System Architecture
This document provides a high-level overview of how the project is structured, including how the local and remote databases synchronize and how data flows through the system.

1. Overview
Single Sauce of Truth is a recipe organizer application designed to:
Collect and organize recipes efficiently,
Handle local offline usage (via a local SQLite DB),
Synchronize changes to a remote MySQL DB for multi-user or cross-device access,
Provide both a web-based interface (Flask) and a desktop/mobile GUI (Kivy).

2. Key Components
UI Layer
Kivy-based Desktop/Mobile App
A local application that interacts with the user and stores data offline in a local SQLite database if desired.
Flask-based Web Interface
Allows users to manage recipes via a browser, reading/writing to the remote MySQL database in real time.

Local Database (SQLite)
Used primarily by the Kivy app for offline functionality or single-device usage.
Stores recipes (in a recipe table) and bridging data (recipe_ingredient), along with optional ingredient, category, and other tables.

Remote Database (MySQL)
Central server that manages shared data across multiple devices or users.
Identical schema (recipe, ingredient, recipe_ingredient, etc.) ensuring consistent structure.
Typically runs on a dedicated host or in Docker Compose, enabling multi-user access.

Synchronization/ETL Logic
Responsible for merging updates from local to remote DB (or vice versa).
Optionally triggered manually by the user (e.g., “Sync Now” button) or automatically at intervals.
Relies on comparing timestamps or row versions to identify changes that must be pushed/pulled.

Back-End Services
The Flask routes in flask_main.py for retrieving or updating recipes.
The Kivy RecipeApp class can also connect directly to MySQL if the user chooses remote usage instead of local usage.
Optionally, a “sync service” (e.g., a Python script or scheduled job) can handle conflicts, merges, or advanced logic like conflict resolution.

3. Data Flow: Local → Remote → Multi-User
Scenario: A user is offline or simply using the local Kivy app for quick access. They add or modify recipes in the local SQLite DB. Later, they go online (or decide to sync):
User → Local DB
The user’s changes (new recipe, updated instructions, new bridging row in recipe_ingredient) are written to SQLite tables.
Local DB → Sync Service
On “Sync Now,” a Python script or an internal function (possibly in the Kivy app) scans for new/modified rows.
It constructs the necessary SQL or API calls to push those changes to the remote MySQL DB.
Remote DB (MySQL)
The remote MySQL server receives these row inserts/updates. If all constraints are met (e.g., valid ingredient_id, etc.), it commits them.
The updated data is now available for other users or devices, which can similarly sync from the remote DB.
Multi-User Sync
Another user logs in via the Flask web interface. They see the newly added or updated recipe rows. They can also add or modify data, which resides in MySQL.
If the first user’s local DB is out of date, the next sync operation fetches changes from MySQL and updates the local SQLite accordingly.
Conflict Handling (We'll have to think about this)
If two offline devices edited the same recipe simultaneously, the sync service may detect collisions (timestamp or row version mismatch).
The system can store the conflicts or pick a “latest wins” approach. The architecture can incorporate more sophisticated conflict resolution if desired.

4. Database Schema
The schema includes:
recipe
Main table for recipe metadata: name, name_es, instructions, cooking_time_minutes, difficulty, source, timestamps, foreign keys to category and user.
ingredient
Table for ingredient references: name, description, possible flavor_profile_id, etc.
recipe_ingredient (bridging)
Many-to-many relationship: references recipe_id and ingredient_id, plus fields like quantity, unit, and optional.
Additional Tables
category, user, cohort, etc., each with relevant foreign key constraints.

5. Implementation Highlights
db/app_tables.py
Contains create_app_tables(...) to define the schema for both MySQL and SQLite, ensuring a consistent structure.
db/db.py
Contains logic for bulk insert (recipes + bridging data) and fetch methods (fetch_recipes_with_ingredients) to handle full recipe info including joined data from recipe_ingredient and ingredient.
db/get_connection.py
Provides get_db_connection(db_type, db_config) for unifying the local/remote DB usage.

kivy_main.py and flask_main.py
Two “front-end” approaches:
Kivy app for a local GUI, offline usage, optional sync.
Flask web app for multi-user or remote usage.
Both import RecipeApp from a shared module, enabling them to call the same insert/fetch logic as needed.
Sync Approach
Currently manual or partially implemented. The user can run a command or click “Sync.”
Future improvements could store last-sync timestamps, track updates in each DB, and auto-resolve conflicts.

6. Future Enhancements
Conflict Resolution: If two offline devices update the same recipe, how do we decide the final version? Provide a user-facing tool or “latest wins.”
Role-Based Access: Enhanced security for multi-user concurrency. The role table references user roles in user.
Ingredient Management: A UI for adding new ingredients, or searching and linking them to recipes, ensuring the bridging row is always valid.
Migration Tools: If the schema changes, a migration approach (Alembic or custom scripts) can help keep local and remote DBs consistent.
Advanced Sync: A dedicated sync service or Cron job that merges changes to a central server, possibly via an API.

7. Diagram

        +-----------+       +----------------+       +---------+
        |   User A  |  ->  |   Kivy App     |  ->   |  SQLite |
        +-----------+       +----------------+       +---------+
                                | (Manual Sync)
                                v
                        +---------------+
                        |   Sync Logic  |
                        +---------------+
                                |
                                v
        +-----------+       +----------------+      +------------+
        |   User B  |  ->  |  Flask (HTTP)  |  ->  | MySQL (Remote)
        +-----------+       +----------------+      +------------+
                                                |
                                                +----> Additional Users
In this architecture, the Sync Logic merges data from the local DB to the remote DB and back. Both Kivy and Flask apps read from the same schema design, ensuring consistent recipe records and bridging.

Conclusion
This architecture supports both local offline usage and remote multi-user usage for Single Sauce of Truth. By separating the UI approach (Kivy vs. Flask) from the underlying data logic (in RecipeApp, db.py), the system remains modular. The sync approach ensures local changes eventually propagate to the remote database, enabling collaborative recipe management while retaining offline capabilities
