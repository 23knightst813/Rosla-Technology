import sqlite3
from werkzeug.security import generate_password_hash
import time
import logging


def set_up_db():
    """
    Set up the database by creating necessary tables if they do not exist.
    """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    #Create the carbon footprint table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carbon_footprint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        footprint REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()


def add_user(email, password, role):
    """
    Add a new user to the database with retry logic for locked database.
    
    Args:
        email (str): The email address of the user.
        password (str): The password provided by the user.
        role (int): The role of the user (0 for regular user, 1 for admin).
            
    Returns:
        bool: True if the user was added successfully, False if the user already exists.
    """
    max_attempts = 3  # Maximum number of attempts to try inserting the user
    attempt = 0  # Current attempt count
    
    while attempt < max_attempts:
        try:
            # Connect to the database with a timeout to handle locked database
            conn = sqlite3.connect('database.db', timeout=20)
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)  # Hash the user's password
            
            # Insert the new user into the users table
            cursor.execute('''
                INSERT INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
            ''', (email, hashed_password, role))
            
            conn.commit()  # Commit the transaction
            logging.info('User added successfully!')  # Log success message
            return True
            
        except sqlite3.IntegrityError:
            # Handle case where the user already exists
            logging.error('User already exists!')  # Log error message
            return False
            
        except sqlite3.OperationalError as e:
            # Handle operational errors such as database being locked
            if "database is locked" in str(e):
                attempt += 1  # Increment the attempt count
                if attempt < max_attempts:
                    logging.warning('Database is locked, retrying...')  # Log warning message
                    time.sleep(1)  # Wait before retrying
                    continue
            raise  # Re-raise the exception if it's not a locked database error
            
        finally:
            if 'conn' in locals():
                conn.close()  # Ensure the database connection is closed
