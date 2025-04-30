
import sqlite3
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

def create_admin_account():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get admin credentials from environment
    admin_email = "admin@example.com"
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_password:
        raise ValueError("ADMIN_PASSWORD not found in .env file")
    
    # Generate secure password hash using Werkzeug's scrypt (default)
    password_hash = generate_password_hash(admin_password)
    
    # Connect to SQLite database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:

        # Insert admin account
        cursor.execute('''
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
        ''', (admin_email, password_hash, True))
        
        conn.commit()
        print(f"Admin account '{admin_email}' created successfully!")
        
    except sqlite3.IntegrityError:
        print(f"Admin account '{admin_email}' already exists")
    finally:
        conn.close()
