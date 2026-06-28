import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()


#=====================================================================
# stablish conection though mysql

def get_connection():
    """Create and return a MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host     = os.getenv("MYSQL_HOST", "localhost"),
            port     = int(os.getenv("MYSQL_PORT", 3306)),
            user     = os.getenv("MYSQL_USER", "root"),
            password = os.getenv("MYSQL_PASSWORD", "3465"),
            database = os.getenv("MYSQL_DATABASE", "wanderai")
        )
        return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
        return None
    
#===================================================================== 
# save data 

def save_chat(session_id, destination, user_query,
              flight_result, hotel_results, activity_results,
              itinerary, budget_estimate, final_plan,
              vibes="", llm_calls=0):
    """Insert a completed trip plan into user_chats."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO user_chats (
                session_id, destination, user_query,
                flight_result, hotel_results, activity_results,
                itinerary, budget_estimate, final_plan,
                vibes, llm_calls
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (
            session_id, destination, user_query,
            flight_result, hotel_results, activity_results,
            itinerary, budget_estimate, final_plan,
            vibes, llm_calls
        )
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid          # return new row ID

    except Error as e:
        print(f"Save chat error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
        
        
#======================================================================
# show the all chats 

def get_all_chats(session_id):
    """Fetch all trips for a session, newest first."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT id, destination, user_query, vibes,
                   llm_calls, created_at
            FROM user_chats
            WHERE session_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(sql, (session_id,))
        return cursor.fetchall()

    except Error as e:
        print(f"Get chats error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

#======================================================================
# show chat by id 

def get_chat_by_id(chat_id, session_id):
    """Fetch one full trip by ID (verify session ownership)."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM user_chats
            WHERE id = %s AND session_id = %s
        """
        cursor.execute(sql, (chat_id, session_id))
        return cursor.fetchone()

    except Error as e:
        print(f"Get chat by ID error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
        
#=====================================================================
# if user want to delete chat 


def delete_chat(chat_id, session_id):
    """Delete a trip (only if it belongs to the session)."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "DELETE FROM user_chats WHERE id = %s AND session_id = %s"
        cursor.execute(sql, (chat_id, session_id))
        conn.commit()
        return cursor.rowcount > 0      # True if deleted

    except Error as e:
        print(f"Delete chat error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
        
        
