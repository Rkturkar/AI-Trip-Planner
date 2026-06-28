from mysql.connector import Error

from Backend.database.connection import get_connection


# ==========================================================
# Save Trip
# ==========================================================

def save_chat(
    session_id,
    destination,
    user_query,
    start_location,
    transport_mode,
    nearest_station,
    booking_url,
    flight_result,
    hotel_results,
    activity_results,
    itinerary,
    budget_estimate,
    final_plan,
    vibes="",
    llm_calls=0,
):
    """
    Save a completed trip into the database.
    """
    conn = get_connection()

    if not conn:
        return None

    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO user_chats (
                session_id,
                destination,
                user_query,
                start_location,
                transport_mode,
                nearest_station,
                booking_url,
                flight_result,
                hotel_results,
                activity_results,
                itinerary,
                budget_estimate,
                final_plan,
                vibes,
                llm_calls
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
        """

        values = (
            session_id,
            destination,
            user_query,
            start_location,
            transport_mode,
            nearest_station,
            booking_url,
            flight_result,
            hotel_results,
            activity_results,
            itinerary,
            budget_estimate,
            final_plan,
            vibes,
            llm_calls,
        )

        cursor.execute(query, values)
        conn.commit()

        return cursor.lastrowid

    except Error as e:
        print(f"Save Chat Error : {e}")
        return None

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# Get All Trips
# ==========================================================

def get_all_chats(session_id):
    """
    Return all trips of a user session.
    """
    conn = get_connection()

    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                destination,
                user_query,
                start_location,
                transport_mode,
                nearest_station,
                booking_url,
                vibes,
                llm_calls,
                created_at
            FROM user_chats
            WHERE session_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(query, (session_id,))

        return cursor.fetchall()

    except Error as e:
        print(f"Get Chats Error : {e}")
        return []

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# Get Single Trip
# ==========================================================

def get_chat_by_id(chat_id, session_id):
    """
    Return a single trip.
    """
    conn = get_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT *
            FROM user_chats
            WHERE id=%s
            AND session_id=%s
        """

        cursor.execute(query, (chat_id, session_id))

        return cursor.fetchone()

    except Error as e:
        print(f"Get Chat Error : {e}")
        return None

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# Delete Trip
# ==========================================================

def delete_chat(chat_id, session_id):
    """
    Delete a trip.
    """
    conn = get_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        query = """
            DELETE FROM user_chats
            WHERE id=%s
            AND session_id=%s
        """

        cursor.execute(query, (chat_id, session_id))
        conn.commit()

        return cursor.rowcount > 0

    except Error as e:
        print(f"Delete Chat Error : {e}")
        return False

    finally:
        cursor.close()
        conn.close()