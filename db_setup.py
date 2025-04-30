import mysql.connector
from mysql.connector import errorcode

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS distributors_db DEFAULT CHARACTER SET 'utf8mb4'")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        create_database(cursor)
        conn.database = 'distributors_db'

        # Create table if it doesn't exist
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS distributors_contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255)  NULL,
                email VARCHAR(255) NULL,
                phone VARCHAR(50) NULL
            )
        '''
        cursor.execute(create_table_query)
        print("Database and table are ready.")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Check your username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist and could not be created.")
        else:
            print(f"An error occurred: {err}")
        exit(1)
