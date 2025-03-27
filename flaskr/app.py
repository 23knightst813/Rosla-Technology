import logging
from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from db import set_up_db, add_user, add_carbon_footprint
from auth import sign_in, get_user_id_by_email
from validation import is_not_empty, is_valid_email, is_secure_password


app = Flask(__name__)
app.secret_key = 'dev' 


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/infoHub')
def infoHub():
    return render_template('InfoHub.html')

@app.route('/cfpCalculater')
def cfpCalculater():
    return render_template('cfpCalculater.html')

@app.route('/cfp_calculator_submit', methods=["GET", "POST"])
def cfp_calculator_submit():
    if request.method == "POST":

        if not session.get("email"):
            flash("You must be logged in to submit your carbon footprint.", "error")
            return redirect(url_for('login'))
        
        else:
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
    return render_template('tracker.html')

@app.route('/solarConsultation')
def solarConsultation():
    return render_template('solarConsultation.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/installation')
def installation():
    return render_template('installation.html')

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
    return render_template("register.html")

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

if __name__ == "__main__":
    set_up_db()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

    # Production server
    # app.run(host="0.0.0.0", port=5000)
    # Devlopment server
    app.run(debug=True)