import sqlite3
from flask import session, flash
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    # Create the carbon footprint table with proper TEXT data types
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carbon_footprint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        footprint REAL NOT NULL,
        transport TEXT NOT NULL,
        energy TEXT NOT NULL,
        waste TEXT NOT NULL,
        diet TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # Create energy bills table - simplified to match actual OCR data availability
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS energy_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        billing_start_date TEXT NOT NULL,
        billing_end_date TEXT NOT NULL,
        electricity_cost REAL,
        gas_cost REAL,
        total_cost REAL,
        provider TEXT,
        filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    ## Create a table to save Online solar assessment data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS solar_assessment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        roof_area REAL,
        orientation TEXT,
        usable_area REAL,
        energy_potential REAL,
        panel_count REAL,
        price_estimate REAL,
        monthly_payment REAL,
        energy_savings REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
                   ''')
    
    # Create a table to save in person consultation 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS in_person_assessment_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        address TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')


    # Create a table to save installation bookings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS installation_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_type TEXT NOT NULL,
        user_email TEXT NOT NULL,
        user_phone TEXT NOT NULL,
        user_address TEXT NOT NULL,
        booking_time DATETIME NOT NULL,
        house_direction TEXT,
        roof_size REAL,      
        ev_charger_type TEXT,
        charger_location TEXT,
        vehicle_model TEXT, 
        request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    ''')

    conn.commit()
    conn.close()



def delete_bookings(booking_id, booking_type):

    try:
        # Connect to the database with a timeout to handle locked database
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        
        if booking_type == 'in_person_assessment':
            cursor.execute('''
                DELETE FROM in_person_assessment_bookings
                WHERE id = ?
            ''', (booking_id,))
            
        elif booking_type == 'installation_request':
            cursor.execute('''
                DELETE FROM installation_requests
                WHERE id = ?
            ''', (booking_id,))
            
        conn.commit()  # Commit the transaction
        logging.info(f'{booking_type} with ID {booking_id} deleted successfully!')
        return True
        
    except Exception as e:
        logging.error(f'Error deleting {booking_type}: {e}')
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()  # Ensure the database connection is closed

def get_all_bookings():
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM installation_requests
            ORDER BY booking_time ASC
        ''')
        installations = cursor.fetchall()


        cursor.execute('''
            SELECT * FROM in_person_assessment_bookings
            ORDER BY date ASC, time ASC
        ''')
        in_person_assessments = cursor.fetchall()
        conn.close()

        logging.log(logging.INFO, f"Fetched {len(installations)} installation requests and {len(in_person_assessments)} in-person assessments.")
        return installations, in_person_assessments



def check_in_person_assessment_booking(user_id):
        # Check if the user has an in-person assessment booking
        conn = None # Initialize conn
        try:
            # Connect to the database with a timeout to handle locked database
            conn = sqlite3.connect('database.db', timeout=20)
            # Set row_factory to access columns by name (though not strictly needed for just checking existence)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get the in-person assessment booking for this user
            cursor.execute('''
                SELECT 1 FROM in_person_assessment_bookings
                WHERE user_id = ?
                LIMIT 1
            ''', (user_id,))

            row = cursor.fetchone()

            if row:
                logging.info(f'In-person assessment booking found for user {user_id}')
                return True  # Booking exists
            else:
                logging.warning(f'No in-person assessment booking found for user {user_id}')
                return False # No booking found

        except Exception as e:
            logging.error(f"Error checking in-person assessment booking for user {user_id}: {e}")
            return False # Return False on error
        finally:
            if conn:
                conn.close() # Ensure connection is closed

def add_in_person_assessment_booking(user_id, date, time, address, email, phone):
    """
    Add a new in-person assessment booking to the database.
    
    Args:
        user_id (int): The ID of the user.
        date (str): The date of the booking.
        time (str): The time of the booking.
        address (str): The address for the assessment.
        email (str): The email address of the user.
        phone (str): The phone number of the user.
            
    Returns:
        bool: True if the entry was added successfully, False otherwise.
    """
    try:
        # Connect to the database with a timeout to handle locked database
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        
        # Check if the time slot is already taken
        cursor.execute('''
            SELECT COUNT(*) FROM in_person_assessment_bookings
            WHERE date = ? AND time = ?
        ''', (date, time))
        count = cursor.fetchone()[0]
        
        if count > 0:
            logging.warning(f'Time slot {date} {time} is already taken!')
            flash('Time slot is already booked. Please choose another time.', 'error')
            return False  # Time slot is already booked
        
        # Insert the new in-person assessment booking into the table
        cursor.execute('''
            INSERT INTO in_person_assessment_bookings (
                user_id, date, time, address, email, phone
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, date, time, address, email, phone))
        
        conn.commit()  # Commit the transaction
        logging.info('In-person assessment booking added successfully!')  # Log success message
        flash('In-person assessment booking added successfully!', 'success')  # Flash success message
        return True
        
    except Exception as e:
        logging.error(f'Error adding in-person assessment data: {e}')  # Log error message
        flash('Error adding in-person assessment data. Please try again.', 'error')  # Flash error message
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()  # Ensure the database connection is closed

def add_solar_assessment(user_id, roof_area, orientation, usable_area, energy_potential, panel_count, price_estimate, monthly_payment, energy_savings):
    """
    Add a new solar assessment entry to the database.
    
    Args:
        user_id (int): The ID of the user.
        roof_area (float): The area of the roof in square meters.
        orientation (str): The orientation of the roof (e.g., South, East).
        usable_area (float): The usable area for solar panels in square meters.
        energy_potential (float): The energy potential from solar panels in kWh.
        panel_count (int): The number of solar panels.
        price_estimate (float): The estimated price for the solar installation.
        monthly_payment (float): The estimated monthly payment for the solar installation.
        energy_savings (float): The estimated energy savings from solar installation.
            
    Returns:
        bool: True if the entry was added successfully, False otherwise.
    """
    try:
        # Connect to the database with a timeout to handle locked database
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        
        # Delete any existing solar assessment for the user
        cursor.execute('''
            DELETE FROM solar_assessment WHERE user_id = ?
        ''', (user_id,))

        # Insert the new solar assessment entry into the solar_assessment table
        cursor.execute('''
            INSERT INTO solar_assessment (
                user_id, roof_area, orientation, usable_area, 
                energy_potential, panel_count, price_estimate, 
                monthly_payment, energy_savings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, roof_area, orientation, usable_area,
            energy_potential, panel_count, price_estimate,
            monthly_payment, energy_savings
        ))
        
        conn.commit()  # Commit the transaction
        logging.info('Solar assessment entry added successfully!')  # Log success message
        return True
        
    except Exception as e:
        logging.error(f'Error adding solar assessment data: {e}')  # Log error message
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()  # Ensure the database connection is closed


def get_user_solar_assessment(user_id):
    """
    Retrieve solar assessment data for a specific user.
    
    Args:
        user_id (int): The ID of the user.
            
    Returns:
        dict: A dictionary containing the user's solar assessment data, or None if not found.
    """
    try:
        # Connect to the database with a timeout to handle locked database
        conn = sqlite3.connect('database.db', timeout=20)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get the solar assessment data for this user
        cursor.execute('''
            SELECT * FROM solar_assessment
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            result = dict(row)  # Convert Row object to dictionary
            logging.info(f'Solar assessment data retrieved successfully for user {user_id}')
            return result  # Return the assessment data
        
        logging.warning(f'No solar assessment data found for user {user_id}')
        return None  # No assessment found for this user
        
    except Exception as e:
        logging.error(f'Error retrieving solar assessment data: {e}')  # Log error message
        return None
        
    finally:
        if 'conn' in locals():
            conn.close()  # Ensure the database connection is closed

def add_carbon_footprint(user_id, date, footprint, transport, energy, waste, diet):
    """
    Add a new carbon footprint entry to the database.
    
    Args:
        user_id (int): The ID of the user.
        date (str): The date of the carbon footprint entry.
        footprint (float): The carbon footprint value.
        transport (str): The transport method used.
        energy (str): The energy source used.
        waste (str): The waste management method used.
        diet (str): The diet type of the user.
            
    Returns:
        bool: True if the entry was added successfully, False if the user does not exist.
    """
    try:
        # Connect to the database with a timeout to handle locked database
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        
        # Insert the new carbon footprint entry into the carbon_footprint table
        cursor.execute('''
            INSERT INTO carbon_footprint (user_id, date, footprint, transport, energy, waste, diet)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, footprint, transport, energy, waste, diet))
        
        conn.commit()  # Commit the transaction
        logging.info('Carbon footprint entry added successfully!')  # Log success message
        return True
        
    except sqlite3.IntegrityError:
        # Handle case where the user does not exist
        logging.error('User does not exist!')  # Log error message
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()  # Ensure the database connection is closed


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

def add_energy_bill(user_id, bill_data, filename=None):
    """
    Add a new energy bill entry to the database based on OCR extracted data.
    
    Args:
        user_id (int): The ID of the user.
        bill_data (dict): The parsed bill data with billing period and costs.
        filename (str, optional): The original filename of the uploaded bill.
            
    Returns:
        bool: True if the entry was added successfully, False otherwise.
    """
    try:
        # Extract data from bill_data
        billing_period = bill_data.get('billingPeriod', {})
        start_date = billing_period.get('startDate', '')
        end_date = billing_period.get('endDate', '')
        
        usage_totals = bill_data.get('usageTotalsFromBill', {})
        electricity_cost = usage_totals.get('electricityCostGBP', 0)
        gas_cost = usage_totals.get('gasCostGBP', 0)
        total_cost = electricity_cost + gas_cost
        
        provider = bill_data.get('provider', 'Unknown')
        
        # Connect to the database
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        
        # Insert the energy bill data
        cursor.execute('''
            INSERT INTO energy_bills (
                user_id, billing_start_date, billing_end_date, 
                electricity_cost, gas_cost, total_cost, provider, filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, start_date, end_date, 
            electricity_cost, gas_cost, total_cost, provider, filename
        ))
        
        conn.commit()
        logging.info(f'Energy bill data added successfully for user {user_id}')
        return True
        
    except Exception as e:
        logging.error(f'Error adding energy bill data: {e}')
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_energy_data(user_id):
    """
    Retrieve energy usage data for a specific user.
    
    Args:
        user_id (int): The ID of the user.
            
    Returns:
        dict: A dictionary containing the user's energy data for charts.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db', timeout=20)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get all energy bills for this user, ordered by date
        cursor.execute('''
            SELECT * FROM energy_bills
            WHERE user_id = ?
            ORDER BY billing_start_date ASC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        
        # Process the data into the required format for the charts
        monthly_usage = []
        month_totals = {}
        total_electricity = 0
        total_gas = 0
        
        for row in rows:
            # Extract date components for grouping by month
            billing_start_date = row['billing_start_date'] or ""
            
            # Skip entries with invalid dates
            if not billing_start_date or len(billing_start_date) < 7:
                logging.warning(f"Skipping energy bill with invalid date: {billing_start_date}")
                continue
                
            month_year = billing_start_date[0:7]  # Format: "YYYY-MM"
            
            # Create a more readable date label (e.g., "Oct 2022")
            import datetime
            try:
                date_obj = datetime.datetime.strptime(month_year, "%Y-%m")
                date_label = date_obj.strftime("%b %Y")
            except ValueError:
                # If date format is invalid, use raw string
                date_label = month_year
                
            # Add costs to monthly totals (safely convert to float in case of None values)
            if month_year not in month_totals:
                month_totals[month_year] = {
                    'date': date_label,
                    'electricity': 0,
                    'gas': 0,
                    'total': 0
                }
            
            electricity_cost = float(row['electricity_cost'] or 0)
            gas_cost = float(row['gas_cost'] or 0)
            
            month_totals[month_year]['electricity'] += electricity_cost
            month_totals[month_year]['gas'] += gas_cost
            month_totals[month_year]['total'] += (electricity_cost + gas_cost)
            
            # Add to overall totals
            total_electricity += electricity_cost
            total_gas += gas_cost
            
        # Convert month_totals to list format for charts
        for month, data in month_totals.items():
            monthly_usage.append({
                'date': data['date'],
                'value': data['total']
            })
            
        # Create category breakdown using the electricity/gas split
        # This is a simplification since we don't have actual usage categories
        category_breakdown = [
            {'category': 'Electricity', 'value': total_electricity},
            {'category': 'Gas', 'value': total_gas}
        ]
        
        # Create the result dictionary
        result = {
            'monthly_usage': monthly_usage,
            'category_breakdown': category_breakdown
        }
        
        return result
        
    except Exception as e:
        logging.error(f'Error retrieving energy data: {e}')
        return {'monthly_usage': [], 'category_breakdown': []}
        
    finally:
        if 'conn' in locals():
            conn.close()

def add_installation_request(user_id, product_type, user_email, user_phone, user_address, booking_time, house_direction=None, roof_size=None, ev_charger_type=None, charger_location=None, vehicle_model=None):
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()

        # Check if the time and date slot is already taken by *any* user.
        cursor.execute('''
            SELECT COUNT(*) FROM installation_requests
            WHERE booking_time = ?
        ''', (booking_time,)) 
        count = cursor.fetchone()[0]

        if count > 0:
            logging.warning(f'Time slot {booking_time} is already taken!')
            flash('Time slot is already booked. Please choose another time.', 'error')
            return False  # Time slot is already booked

        # Insert the installation request into the table
        cursor.execute('''
            INSERT INTO installation_requests (
                user_id, product_type, user_email, user_phone,
                user_address, booking_time, house_direction,
                roof_size, ev_charger_type, charger_location, vehicle_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, product_type, user_email, user_phone,
            user_address, booking_time, house_direction,
            roof_size, ev_charger_type, charger_location, vehicle_model
        ))

        conn.commit()  # Commit the transaction
        logging.info('Installation request added successfully!')  # Log success message
        return True
    except sqlite3.IntegrityError:
        # Handle case where the user does not exist (foreign key constraint)
        logging.error(f'User with ID {user_id} does not exist!')
        flash('User does not exist!', 'error')  # Flash error message
        return False
    except sqlite3.OperationalError as e:
        # Handle operational errors such as database being locked
        if "database is locked" in str(e):
            logging.error('Database is locked!')
            flash('Database is locked! Please try again later.', 'error')  # Flash error message
        else:
            logging.error(f'Error adding installation request: {e}')
            flash('Error adding installation request. Please try again.', 'error')  # Flash error message
        return False
    except Exception as e:  # Catch any other potential exceptions
        logging.error(f'An unexpected error occurred: {e}')
        flash('An unexpected error occurred. Please try again.', 'error')
        return False
    finally:
        if conn:
            conn.close()

def get_user_installation_requests(user_id):
    """
    Retrieve installation requests for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of installation requests (as Row objects) for the user.
              booking_time will be a datetime object.
    """
    conn = None
    try:
        # Add detect_types to automatically convert DATETIME columns to datetime objects
        conn = sqlite3.connect('database.db', timeout=20, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row # Return rows that can be accessed by column name
        cursor = conn.cursor()

        # Ensure the column name in the query matches the declared type (DATETIME or TIMESTAMP)
        # The type is declared as DATETIME in the CREATE TABLE statement.
        cursor.execute('''
            SELECT id, user_id, product_type, user_email, user_phone, user_address,
                   booking_time, house_direction, roof_size, ev_charger_type,
                   charger_location, vehicle_model, request_timestamp
            FROM installation_requests
            WHERE user_id = ?
            ORDER BY booking_time ASC
        ''', (user_id,))
        installations = cursor.fetchall()
        logging.info(f"Fetched {len(installations)} installation requests for user {user_id}.")
        return installations
    except Exception as e:
        logging.error(f"Error fetching installation requests for user {user_id}: {e}")
        return [] # Return empty list on error
    finally:
        if conn:
            conn.close()

def get_user_in_person_assessments(user_id):
    """
    Retrieve in-person assessment bookings for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of in-person assessment bookings (as Row objects) for the user.
    """
    conn = None
    try:
        # Add detect_types here as well if date/time conversion is needed later
        # Note: 'date' and 'time' columns are TEXT, so they won't be auto-converted
        conn = sqlite3.connect('database.db', timeout=20, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row # Return rows that can be accessed by column name
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM in_person_assessment_bookings
            WHERE user_id = ?
            ORDER BY date ASC, time ASC
        ''', (user_id,))
        assessments = cursor.fetchall()
        logging.info(f"Fetched {len(assessments)} in-person assessments for user {user_id}.")
        return assessments
    except Exception as e:
        logging.error(f"Error fetching in-person assessments for user {user_id}: {e}")
        return [] # Return empty list on error
    finally:
        if conn:
            conn.close()

def verify_password(user_id, password):
    """
    Verify the provided password against the stored hash for the user.

    Args:
        user_id (int): The ID of the user.
        password (str): The password to verify.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            stored_hash = result[0]
            return check_password_hash(stored_hash, password)
        return False # User not found or no password hash stored
    except Exception as e:
        logging.error(f"Error verifying password for user {user_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_user_email(user_id, new_email):
    """
    Update the email address for a specific user.

    Args:
        user_id (int): The ID of the user.
        new_email (str): The new email address.

    Returns:
        bool: True if the email was updated successfully, False otherwise (e.g., email exists).
    """
    conn = None
    try:
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()

        # Check if the new email already exists for another user
        cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (new_email, user_id))
        if cursor.fetchone():
            logging.warning(f"Attempt to update email for user {user_id} failed: email '{new_email}' already exists.")
            flash("Email address already in use by another account.", "error")
            return False

        # Update the email
        cursor.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            logging.info(f"Email updated successfully for user {user_id}.")
            return True
        else:
            logging.warning(f"Attempt to update email for non-existent user ID {user_id}.")
            return False # User ID might not exist
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            logging.error("Database is locked during email update.")
            flash("Database error, please try again later.", "error")
        else:
            logging.error(f"Error updating email for user {user_id}: {e}")
            flash("An error occurred while updating email.", "error")
        return False
    except Exception as e:
        logging.error(f"Error updating email for user {user_id}: {e}")
        flash("An error occurred while updating email.", "error")
        return False
    finally:
        if conn:
            conn.close()

def update_user_password(user_id, new_password):
    """
    Update the password for a specific user.

    Args:
        user_id (int): The ID of the user.
        new_password (str): The new password.

    Returns:
        bool: True if the password was updated successfully, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect('database.db', timeout=20)
        cursor = conn.cursor()
        new_password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            logging.info(f"Password updated successfully for user {user_id}.")
            return True
        else:
            logging.warning(f"Attempt to update password for non-existent user ID {user_id}.")
            return False # User ID might not exist
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            logging.error("Database is locked during password update.")
            flash("Database error, please try again later.", "error")
        else:
            logging.error(f"Error updating password for user {user_id}: {e}")
            flash("An error occurred while updating password.", "error")
        return False
    except Exception as e:
        logging.error(f"Error updating password for user {user_id}: {e}")
        flash("An error occurred while updating password.", "error")
        return False
    finally:
        if conn:
            conn.close()
