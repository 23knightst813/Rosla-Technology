import logging
from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from db import set_up_db, add_user
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

@app.route('/cfp_calculator_submit')
def cfp_calculator_submit():
    return render_template('cfp_calculator_submit.html')

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