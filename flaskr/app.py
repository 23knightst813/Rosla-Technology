import logging
from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == "__main__":
    # set_up_db()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    # Production server
    # app.run(host="0.0.0.0", port=5000)
    # Devlopment server
    app.run(debug=True)