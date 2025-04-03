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

    conn.commit()
    conn.close()


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

def add_carbon_footprint(user_id, date, footprint, transport, energy, waste, diet):
    """
    Add a new carbon footprint entry to the database and ensuring the user can only have one entry at a time.
    
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
        
        # Delete the last carbon footprint entry for the user
        
        cursor.execute('''
            DELETE FROM carbon_footprint
            WHERE user_id = ?
        ''', (user_id,))
        
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
