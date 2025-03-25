import logging
from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify

app = Flask(__name__, static_folder='../static')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    # set_up_db()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    # Production server
    app.run(host="0.0.0.0", port=5000)
    # Devlopment server
    # app.run(debug=True)