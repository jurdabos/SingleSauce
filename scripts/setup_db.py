from db.app_tables import create_app_tables
from db.db import db_configuration
from db.get_connection import get_db_connection

# MySQL usage
conn_mysql = get_db_connection("mysql", db_configuration)
create_app_tables(conn_mysql, db_type="mysql")
conn_mysql.close()

# SQLite usage
conn_sqlite = get_db_connection("sqlite", db_configuration)
create_app_tables(conn_sqlite, db_type="sqlite")
conn_sqlite.close()
