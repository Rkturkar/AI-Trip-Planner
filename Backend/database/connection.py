import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Create and return a MySQL database connection.
    Returns:
        mysql.connector.connection.MySQLConnection | None
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "3465"),
            database=os.getenv("MYSQL_DATABASE", "wanderai"),
        )

        return connection

    except Error as e:
        print(f"MySQL Connection Error: {e}")
        return None
    
