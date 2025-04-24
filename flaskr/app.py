import logging
import os
import secrets
import string
from datetime import date, datetime
import logging

# --- Make sure get_all_bookings is imported ---
from flask import Flask, make_response, render_template, request, flash, redirect, session, url_for, jsonify
from db import (
    set_up_db, add_user, add_carbon_footprint, add_energy_bill,
    get_user_energy_data, add_solar_assessment, add_in_person_assessment_booking,
    add_installation_request, check_in_person_assessment_booking, get_all_bookings,
    delete_bookings,
    get_user_installation_requests,
    get_user_in_person_assessments,
    verify_password,
    update_user_email,
    update_user_password 
)
from auth import sign_in, get_user_id_by_email
from validation import is_not_empty, is_valid_email, is_secure_password, is_valid_phone_number
from tracker import save_uploaded_file, ocr_process_file, gemini_format
from consultation import solar_potential

app = Flask(__name__)
app.secret_key = 'dev' 

# Add min function to the Jinja2 environment
app.jinja_env.globals.update(min=min)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/infoHub')
def infoHub():
    return render_template('InfoHub.html')

@app.route('/cfpCalculater')
def cfpCalculater():
    if not session.get("email"):
        flash("You must be logged in to submit your carbon footprint.", "error")
        return redirect(url_for('login'))
    else:
        return render_template('cfpCalculater.html')

@app.route('/cfp_calculator_submit', methods=["GET", "POST"])
def cfp_calculator_submit():
    if request.method == "POST":

        
            logging.debug("User is logged in. Proceeding with carbon footprint calculation.")
            # Extract form data
            diet = request.form.get("diet")
            transport = request.form.get("transport")
            energy = request.form.get("energy") 
            waste = request.form.get("waste")
            
            # Log the received data
            logging.debug(f"Received CFP data - Diet: {diet}, Transport: {transport}, Energy: {energy}, Waste: {waste}")
            
            # Initialise emissions (tonnes CO2e per year) for each category
            diet_emissions = 0
            transport_emissions = 0
            energy_emissions = 0
            waste_emissions = 0
            
            # Calculate diet emissions
            # Here, a 'Carnivore' diet is estimated to add around 3.0 tonnes CO2e per year.
            if diet and diet.lower() == "carnivore":
                diet_emissions = 3.0
            else:
                # Provide default or additional cases as needed
                diet_emissions = 2.0
            
            # Calculate transport emissions
            # 'Car' usage contributes roughly 2.5 tonnes CO2e annually.
            if transport and transport.lower() == "car":
                transport_emissions = 2.5
            else:
                transport_emissions = 1.5
            
            # Calculate energy usage emissions
            # 'High' energy usage is estimated to add about 3.5 tonnes CO2e per year.
            if energy and energy.lower() == "high":
                energy_emissions = 3.5
            elif energy and energy.lower() == "medium":
                energy_emissions = 2.0
            elif energy and energy.lower() == "low":
                energy_emissions = 1.0
            else:
                energy_emissions = 2.0
            
            # Calculate waste management emissions
            # 'No Recycling' might add approximately 0.5 tonnes CO2e per year.
            if waste and waste.lower() == "no recycling":
                waste_emissions = 0.5
            elif waste and waste.lower() == "recycling":
                waste_emissions = 0.2
            else:
                waste_emissions = 0.5
            
            # Total carbon footprint estimate (tonnes CO2e per year)
            total_emissions = diet_emissions + transport_emissions + energy_emissions + waste_emissions
            
            # Add to database

            user_id = get_user_id_by_email()
            if user_id:
                # Get the current date
                from datetime import datetime

                date = datetime.now().strftime("%Y-%m-%d")
                
                # Add carbon footprint entry to the database
                if not add_carbon_footprint(user_id, date, total_emissions, transport, energy, waste, diet):
                    flash("Error adding carbon footprint entry.", "error")
                    return redirect(url_for('cfpCalculater'))
            else:
                flash("User not found. Please log in.", "error")
                return redirect(url_for('login'))
            

            logging.debug(f"Total calculated emissions: {total_emissions} tonnes CO2e per year")
            
            # Pass data to the template (including the calculated total)
            return render_template('cfp_calculator_submit.html', 
                                diet=diet,
                                transport=transport,
                                energy=energy,
                                waste=waste,
                                total_emissions=total_emissions)

        
    # If GET request, redirect back to calculator
    return redirect(url_for('cfpCalculater'))

@app.route('/tracker')
def tracker():
    if not session.get("email"):
        flash("You must be logged in to view your energy tracker.", "error")
        return redirect(url_for('login'))
    
    # Get user energy data for the charts
    user_id = get_user_id_by_email()
    if user_id:
        energy_data = get_user_energy_data(user_id)
        return render_template('tracker.html', energy_data=energy_data)
    else:
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('login'))

@app.route('/tracker_upload_file', methods=['POST'])
def upload_file():
    if not session.get("email"):
        flash("You must be logged in to upload energy bills.", "error")
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file part in the request', 'error')
        return redirect(url_for('tracker'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('tracker'))
    
    user_id = get_user_id_by_email()
    if not user_id:
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('login'))
    
    try:
        # Save the uploaded file
        filepath = save_uploaded_file(file)
        if not filepath:
            flash("Error saving file. Please try again with a supported file type.", "error")
            return redirect(url_for('tracker'))
        
        # Process the file with OCR
        ocr_result = ocr_process_file(filepath)
        
        # Extract structured data using Gemini AI
        bill_data = gemini_format(ocr_result)
        
        if not bill_data or not isinstance(bill_data, list) or len(bill_data) == 0:
            flash("Unable to extract data from the uploaded bill. Please try another file.", "error")
            return redirect(url_for('tracker'))
        
        # Store the first result in the database
        success = add_energy_bill(
            user_id=user_id,
            bill_data=bill_data[0],
            filename=file.filename
        )
        
        if success:
            flash("Energy bill successfully processed and data added to your tracker.", "success")
        else:
            flash("Error storing energy data. Please try again.", "error")
            
    except Exception as e:
        logging.error(f"Error processing bill: {str(e)}")
        flash("Error processing bill. Please try again with a clearer image.", "error")
        
    return redirect(url_for('tracker'))

@app.route('/solarConsultation', methods=['GET', 'POST'])
def solarConsultation():
    if request.method == 'POST':
        postcode = request.form.get('postcode')
        selected_address = request.form.get('selected_address')
        
        # Validate submission
        if not selected_address:
            flash("Please enter your postcode/address and select a suggestion from the list.", "error")
            return redirect(url_for('solarConsultation'))
        
        if not postcode or postcode != selected_address:
            flash("Please select a valid address suggestion from the list. Do not manually edit after selecting.", "error")
            return redirect(url_for('solarConsultation'))
        
        try:
            # Call solar_potential function with the selected address
            result = solar_potential(selected_address)
            
            if result:
                # Unpack the tuple returned by solar_potential
                area, orientation, usable_area, energy_potential, panel_count, price_estimate, monthly_payment, energy_savings = result
                
                # Store results in session for display - use consistent format with auth.py
                session['solar_results'] = {
                    'address': selected_address,
                    'area': area,
                    'orientation': orientation,
                    'usable_area': usable_area,
                    'energy_potential': energy_potential,
                    'panel_count': int(panel_count),
                    'price_estimate': price_estimate,
                    'monthly_payment': monthly_payment,
                    'energy_savings': energy_savings
                }

                # Store the results in the database
                user_id = get_user_id_by_email()
                if user_id:  # Only add to database if user is logged in
                    add_solar_assessment(
                        user_id=user_id,
                        roof_area=area,
                        orientation=orientation,
                        usable_area=usable_area,
                        energy_potential=energy_potential,
                        panel_count=panel_count,
                        price_estimate=price_estimate,
                        monthly_payment=monthly_payment,
                        energy_savings=energy_savings
                    )
                    flash("Solar assessment completed successfully!", "success")
                else:
                    flash("Solar assessment completed but not saved to your account. Please log in to save your results.", "warning")
            else:
                flash("Unable to calculate solar potential for this address.", "error")
        except Exception as e:
            flash(f"Error processing solar assessment: {str(e)}", "error")
            logging.error(f"Solar assessment error: {str(e)}")
        
        return redirect(url_for('solarConsultation'))

    if not session.get("email"):
        flash("You must be logged in to find to that", "error")
        return redirect(url_for('login'))
    else:
        # GET request handling - pass any stored results to the template
        solar_results = session.get('solar_results', None)
        return render_template('solarConsultation.html', solar_results=solar_results)
    
@app.route('/personConsultation', methods=['GET', 'POST'])
def personConsultation():
    if request.method == 'POST':
        # Get the form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        booking_date_str = request.form.get('date') # Renamed to avoid conflict with date module
        time = request.form.get('time')

        logging.debug(f"Received form data - Name: {name}, Phone: {phone}, Date: {booking_date_str}, Time: {time}")

        # Validate the form data
        if not all([is_not_empty(name), is_not_empty(phone), is_not_empty(booking_date_str), is_not_empty(time)]):
            flash("All fields are required", "error")
            return redirect(url_for('personConsultation'))

        if not is_valid_phone_number(phone):
            flash("Invalid phone number format", "error")
            return redirect(url_for('personConsultation'))

        # Convert booking_date_str to date object for comparison
        try:
            booking_date = date.fromisoformat(booking_date_str)
            today_date = date.today()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('personConsultation'))

        if booking_date < today_date:
            flash("Please select a date from today onwards.", "error")
            return redirect(url_for('personConsultation'))

        if time < "09:00" or time > "17:00":
            flash("Please select a time between 09:00 and 17:00.", "error")
            return redirect(url_for('personConsultation'))

        # Get Extra Data From Session
        address = session.get('solar_results', {}).get('address')
        email = session.get('email')

        # Ensure user is logged in before attempting to book
        user_id = get_user_id_by_email()
        if not user_id:
            flash("You must be logged in to book a consultation.", "error")
            return redirect(url_for('login')) 

        # Add the data to the session
        session['in_person_assessment'] = {
            'name': name,
            'phone': phone,
            'booking_date': booking_date_str,
            'time': time,
            'address': address,
            'email': email
        }

        # Add the data to the database
        if add_in_person_assessment_booking(user_id, booking_date_str, time, address, email, phone) == False:
            return redirect(url_for('personConsultation', _anchor='consultation'))
        else:
            return redirect(url_for('personConsultation'))


    # --- GET Request Logic ---
    # This part runs only if request.method is 'GET'

    # 1. Get the original data from session
    solar_data = session.get('solar_results')

    if not solar_data:
        flash('Solar assessment data not found. Please complete the assessment first.', 'warning')
        return redirect(url_for('solarConsultation'))

    # 2. Create the NEW dictionary with the keys the template expects
    try:
        predictions_data = {
            'price': solar_data.get('price_estimate', 0),
            'financing': f"£{solar_data.get('monthly_payment', 0):.2f} / Month", # Format the financing string
            'generation': solar_data.get('energy_potential', 0),
            'savings': solar_data.get('energy_savings', 0)
        }
    except (KeyError, TypeError, ValueError) as e: # Catch potential errors during mapping/formatting
        flash(f'Error processing solar data ({e}). Please try the assessment again.', 'error')
        logging.error(f"Error mapping solar data in personConsultation: {e}, Data: {solar_data}")
        return redirect(url_for('solarConsultation'))

    # 4. Pass the NEW dictionary using the variable name 'predictions'
    return render_template('personConsultation.html', predictions=predictions_data)




@app.route('/dashboard')
def dashboard():
    # --- Require Login ---
    if not session.get("email"):
        flash("You must be logged in to view the dashboard.", "error")
        return redirect(url_for('login'))

    user_id = get_user_id_by_email()
    if not user_id:
        flash("User not found. Please log in again.", "error")
        session.clear() # Clear potentially corrupted session
        return redirect(url_for('login'))

    # --- Fetch Data for Dashboard ---
    energy_data = get_user_energy_data(user_id)
    solar_results = session.get('solar_results', None) # Get solar results from session
    installations = get_user_installation_requests(user_id) # Fetch user's installations
    in_person_assessments = get_user_in_person_assessments(user_id) # Fetch user's assessments

    # --- Render Template with Data ---
    return render_template(
        'dashboard.html',
        energy_data=energy_data,
        solar_results=solar_results,
        installations=installations,
        in_person_assessments=in_person_assessments
    )

# --- Add a new route to handle account updates (implementation needed) ---
@app.route('/update_account', methods=['POST'])
def update_account():
    if not session.get("email"):
        flash("You must be logged in.", "error")
        return redirect(url_for('login'))

    user_id = get_user_id_by_email()
    if not user_id:
        flash("User not found.", "error")
        return redirect(url_for('login'))

    current_password = request.form.get('current_password')
    new_email = request.form.get('new_email')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # --- Basic Validation ---
    if not is_not_empty(current_password):
        flash("Current password is required to make changes.", "error")
        return redirect(url_for('dashboard'))

    # --- Password Verification ---
    if not verify_password(user_id, current_password): # Use the imported function
       flash("Incorrect current password.", "error")
       return redirect(url_for('dashboard'))

    email_updated = False
    password_updated = False

    # --- Update Email ---
    if is_not_empty(new_email):
        if not is_valid_email(new_email):
            flash("Invalid new email format.", "error")
            return redirect(url_for('dashboard'))
        # --- Call DB function to update email ---
        if update_user_email(user_id, new_email): # Use the imported function
            session['email'] = new_email # Update session email
            email_updated = True
        else:
            # Flash message is handled within update_user_email
            return redirect(url_for('dashboard'))


    # --- Update Password ---
    if is_not_empty(new_password):
        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for('dashboard'))
        if not is_secure_password(new_password):
             flash(
                "New password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.",
                "error"
            )
             return redirect(url_for('dashboard'))
        # --- Call DB function to update password ---
        if update_user_password(user_id, new_password): # Use the imported function
            password_updated = True
        else:
            # Flash message is handled within update_user_password
            return redirect(url_for('dashboard'))

    # --- Flash success messages ---
    if email_updated and password_updated:
        flash("Email and password updated successfully.", "success")
    elif email_updated:
        flash("Email updated successfully.", "success")
    elif password_updated:
        flash("Password updated successfully.", "success")
    elif not is_not_empty(new_email) and not is_not_empty(new_password):
         flash("No changes were submitted.", "info")


    # --- Redirect back to dashboard ---
    return redirect(url_for('dashboard'))


@app.route('/installation', methods=['GET', 'POST']) # Add POST method
def installation():
    # --- Require Login ---
    if not session.get("email"):
        flash("You must be logged in to request installation.", "error")
        return redirect(url_for('login'))
    
    # -- Require In Person Assessment ---

    if check_in_person_assessment_booking(get_user_id_by_email()) == False:
        flash("You must complete an in-person assessment before requesting installation.", "error")
        return redirect(url_for('personConsultation'))

    if request.method == 'POST':
        # --- POST Request Logic ---

        # --- Get User ID (moved inside POST block) ---
        user_id = get_user_id_by_email()
        if not user_id:
            # This case should ideally not happen if the initial check passes,
            # but it's good practice to handle it.
            flash("User session error. Please log in again.", "error")
            return redirect(url_for('login'))

        # --- Get Common Form Data ---
        product_type = request.form.get('product')
        user_email = request.form.get('email')
        user_phone = request.form.get('phone')
        user_address = request.form.get('address') # Corrected typo from 'adress'
        booking_time_str = request.form.get('booking_time')

        # --- Get Solar Specific Data (if product is 'solar') ---
        house_direction = None
        roof_size = None
        if product_type == 'solar':
            house_direction = request.form.get('house-direction')
            roof_size_str = request.form.get('roof-size')
            try:
                roof_size = float(roof_size_str) if roof_size_str else None
            except ValueError:
                flash("Invalid roof size format. Please enter a number.", "error")
                return redirect(url_for('installation'))


        # --- Get EV Specific Data (if product is 'ev_chargers') ---
        ev_charger_type = None
        charger_location = None
        vehicle_model = None

        if product_type == 'ev_chargers':
            ev_charger_type = request.form.get('ev_charger_type')
            charger_location = request.form.get('charger_location')
            vehicle_model = request.form.get('vehicle_model')

        logging.debug(f"Received installation request - Product: {product_type}, Email: {user_email}, Phone: {user_phone}, Address: {user_address}, Booking Time: {booking_time_str}")

        # --- Validate Common Form Data ---
        # Check user_address as well
        if not all([is_not_empty(product_type), is_not_empty(user_email), is_not_empty(user_phone), is_not_empty(user_address), is_not_empty(booking_time_str)]):
            flash("All fields are required", "error")
            return redirect(url_for('installation'))
        # Validate email and phone number formats
        if not is_valid_email(user_email):
            flash("Invalid email address", "error")
            return redirect(url_for('installation'))
        if not is_valid_phone_number(user_phone):
            flash("Invalid phone number format", "error")
            return redirect(url_for('installation'))
        # Validate booking time
        try:
            # --- Use booking_datetime for validation and DB call ---
            booking_datetime = datetime.fromisoformat(booking_time_str)
            now = datetime.now()

            # Check if the booking is after today and within the allowed time range
            # Compare date parts only for "today onwards" check
            if booking_datetime.date() < now.date():
                flash("Please select a booking date from today onwards.", "error")
                return redirect(url_for('installation'))

            # Compare time parts for the time range check
            if not (datetime.strptime("09:00", "%H:%M").time() <= booking_datetime.time() <= datetime.strptime("17:00", "%H:%M").time()):
                 flash("Please select a booking time between 09:00 and 17:00.", "error")
                 return redirect(url_for('installation'))

        except ValueError:
            flash("Invalid booking time format. Please use the date/time picker.", "error")
            return redirect(url_for('installation'))

        # --- Call DB function with correct arguments ---
        success = add_installation_request(
            user_id=user_id,
            product_type=product_type,
            user_email=user_email,
            user_phone=user_phone,
            user_address=user_address,
            booking_time=booking_datetime, # Pass the datetime object
            house_direction=house_direction, # Pass correct variable
            roof_size=roof_size, # Pass correct variable
            ev_charger_type=ev_charger_type, # Pass correct variable
            charger_location=charger_location, # Pass correct variable
            vehicle_model=vehicle_model # Pass correct variable
        )

        # --- Handle DB function result ---
        if success:
            flash(f"Installation request for {product_type.replace('_', ' ').title()} submitted successfully!", "success")
            return redirect(url_for('dashboard')) # Redirect to dashboard on success
        else:
            # Error flash message is handled within add_installation_request
            return redirect(url_for('installation')) # Stay on installation page on failure


    # --- GET Request ---
    # Fetch data needed to pre-fill the form
    solar_data = session.get('solar_results')
    user_email = session.get('email') # Get email from session for GET request

    # Pass fetched data to the template
    return render_template('installation.html', solar_data=solar_data, user_email=user_email)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        # Validate input fields
        if not all([is_not_empty(email), is_not_empty(password)]):
            flash("All fields are required", "error")
            return redirect("/login")

        if not is_valid_email(email):
            flash("Invalid email address", "error")
            return redirect("/login")
            
        return sign_in(email, password)
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration. Validate input, check for existing account, and add new user to the database.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        role = 0  # Default role for new users

        # Validate input fields
        if not all([is_not_empty(email), is_not_empty(password)]):
            flash("All fields are required", "error")
            return redirect("/register")

        if not is_valid_email(email):
            flash("Invalid email address", "error")
            return redirect("/register")

        if password != password2:
            flash("Passwords do not match", "error")
            return redirect("/register")

        if not is_secure_password(password):
            flash(
                "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.",
                "error"
            )
            return redirect("/register")

        # Add user to the database
        if not add_user(email, password, role):
            flash("Account already exists", "error")
            return redirect("/register")
        flash("Registration successful.", "success")
        sign_in(email, password)
        return redirect("/")
    # Generate a secure example password
    secure_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))

            

    return render_template("register.html", example_password=secure_password)

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is logged in and has admin privileges
    if not session.get("email") or session.get("role") != True:
        flash("You do not have permission to access this page.", "error")
        return redirect("/login")

    # Get Booking Data
    # --- Fetch bookings ---
    try:
        installations, in_person_assessments = get_all_bookings()
        logging.info(f"Admin dashboard: Fetched {len(installations)} installations and {len(in_person_assessments)} assessments.")
    except Exception as e:
        logging.error(f"Error fetching bookings for admin dashboard: {e}")
        flash("Error fetching booking data.", "error")
        installations = []
        in_person_assessments = []


    # --- Pass data to template ---
    return render_template('adminDashboard.html',
                           installations=installations,
                           in_person_assessments=in_person_assessments)

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    # --- Check if user is logged in ---
    if not session.get("email"):
        flash("You must be logged in to delete bookings.", "error")
        return redirect(url_for('login'))

    user_id = get_user_id_by_email()
    if not user_id:
        flash("User not found.", "error")
        return redirect(url_for('login'))

    booking_id = request.form.get('booking_id')
    booking_type = request.form.get('booking_type')

    if not booking_id or not booking_type:
        flash("Invalid request. Missing booking information.", "error")
        # Redirect to dashboard for user, admin_dashboard for admin
        redirect_url = url_for('admin_dashboard') if session.get("role") else url_for('dashboard')
        return redirect(redirect_url)

    try:
        booking_id = int(booking_id) # Ensure booking_id is an integer
    except ValueError:
        flash("Invalid booking ID.", "error")
        redirect_url = url_for('admin_dashboard') if session.get("role") else url_for('dashboard')
        return redirect(redirect_url)

    if booking_type not in ['installation_request', 'in_person_assessment']:
        flash("Invalid booking type.", "error")
        redirect_url = url_for('admin_dashboard') if session.get("role") else url_for('dashboard')
        return redirect(redirect_url)

    # --- Authorization Check: User must own the booking OR be an admin ---
    can_delete = False
    if session.get("role") == True: # Admin can delete any booking
        can_delete = True
    else: # Regular user check
        conn = None
        try:
            conn = sqlite3.connect('database.db', timeout=10)
            cursor = conn.cursor()
            table_name = "installation_requests" if booking_type == 'installation_request' else "in_person_assessment_bookings"
            cursor.execute(f"SELECT user_id FROM {table_name} WHERE id = ?", (booking_id,))
            result = cursor.fetchone()
            if result and result[0] == user_id:
                can_delete = True
        except Exception as e:
            logging.error(f"Error checking booking ownership for user {user_id}, booking {booking_id}: {e}")
            flash("Error verifying booking ownership.", "error")
        finally:
            if conn:
                conn.close()

    if not can_delete:
        flash("You do not have permission to delete this booking.", "error")
        redirect_url = url_for('admin_dashboard') if session.get("role") else url_for('dashboard')
        return redirect(redirect_url)

    # --- Call the delete function from db.py ---
    success = delete_bookings(booking_id, booking_type) # delete_bookings function already exists

    if success:
        flash(f"{booking_type.replace('_', ' ').title()} deleted successfully.", "success")
    else:
        # Error flash is handled within delete_bookings or above checks
        pass # Avoid double flashing

    # --- Redirect back to the appropriate dashboard ---
    redirect_url = url_for('admin_dashboard') if session.get("role") else url_for('dashboard')
    return redirect(redirect_url)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('index'))

@app.route('/ev_chargers')
def ev_chargers():
    return render_template('infoPages/evChargers.html')

@app.route('/green_energy')
def green_energy():
    return render_template('infoPages/greenEnergy.html')

@app.route('/smart_home')
def smart_home():
    return render_template('infoPages/smartHome.html')

@app.route('/reduce_carbon_footprint')
def energy_tips():
    return render_template('infoPages/reduceCarbonFootprint.html')

# Define the set_cookie route
@app.route('/set_cookie', methods=['POST'])
def set_cookie():
    next_url = request.referrer or url_for('index')  # Get the referring page or default to index
    response = make_response(redirect(next_url))
    response.set_cookie('cookie_consent', 'true', max_age=60*60*24*365)  # 1 year
    return response

# Define error handlers for various HTTP status codes
@app.errorhandler(404)
def page_not_found(e):
    flash('Page not found', 'error')
    return redirect("/")  
@app.errorhandler(500)
def internal_server_error(e):
    flash('Internal server error', 'error')
    return redirect("/")
@app.errorhandler(405)
def method_not_allowed(e):
    flash('Method not allowed', 'error')
    return redirect("/")
@app.errorhandler(403)
def forbidden(e):
    flash('Access denied', 'error')
    return redirect("/")
@app.errorhandler(401)
def unauthorized(e):
    flash('Unauthorized access', 'error')
    return redirect("/")
@app.errorhandler(400)
def bad_request(e):
    flash('Bad request', 'error')
    return redirect("/")
@app.errorhandler(413)
def request_entity_too_large(e):
    flash('Request entity too large', 'error')
    return redirect("/")
# @app.errorhandler(Exception)
# def handle_exception(e):
#     flash('An unexpected error occurred. Please try again later.', 'error')
#     return redirect("/")


if __name__ == "__main__":
    set_up_db()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

    # Production server
    # app.run(host="0.0.0.0", port=5000)
    # Devlopment server
    app.run(debug=True)