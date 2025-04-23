import logging
from flask import session, flash, redirect
import sqlite3
from werkzeug.security import check_password_hash
from db import get_user_solar_assessment

def get_user_id_by_email():
    """
    Retrieve the user ID based on the email stored in the session.
    
    Returns:
        int: The user ID if found, otherwise None.
    """
    try:
        email = session.get("email")
        if not email:
            flash("User not logged in", "error")
            logging.error("User not logged in")
            return None
            
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            flash("User not found", "error")
            logging.error("User not found")
            return None
            
        return result[0]
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
        logging.error(f"Database error: {str(e)}")
        return None

def sign_in(email, password):
    """
    Authenticate a user by checking their email and password against the database.
    
    Args:
        email (str): The email address of the user.
        password (str): The password provided by the user.
    
    Returns:
        redirect: Redirects to the appropriate page based on authentication success.
    """
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    query = """SELECT email, password_hash, role FROM users WHERE email = ?"""
    cur.execute(query, (email,))
    user = cur.fetchone()
    conn.close()

    if user:
        print(f"User found: {user[0]}, Hashed Password: {user[1]}")
        if check_password_hash(user[1], password):
            session["email"] = user[0]
            session["role"] = bool(user[2])
            flash("Logged in successfully!", "success")
            user_id = get_user_id_by_email()
            logging.info(f"User ID: {user_id}")
            
            # Get solar assessment and store in session if available
            solar_data = get_user_solar_assessment(user_id)
            if solar_data:
                # Use 'solar_results' as the session key to match what's used in app.py
                session['solar_results'] = {
                    'address': "Previously assessed property",
                    'area': solar_data['roof_area'],
                    'orientation': solar_data['orientation'],
                    'usable_area': solar_data['usable_area'],
                    'energy_potential': solar_data['energy_potential'],
                    'panel_count': int(solar_data['panel_count']),
                    'price_estimate': solar_data['price_estimate'],
                    'monthly_payment': solar_data['monthly_payment'],
                    'energy_savings': solar_data['energy_savings']
                }
                logging.info("Loaded previous solar assessment into session under 'solar_results' key")
            
            if session["role"] == 1:
                return redirect("/admin_dashboard")
            return redirect("/")
        else:
            flash("Invalid password", "error")
            logging.error("Invalid password")
            return redirect("/login")
    else:
        flash("User not found", "error")
        logging.error("User not found")
        return redirect("/login")

