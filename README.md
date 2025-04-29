# Rosla Technologies
### Done In My Final Exam, In Exam Conditions, Meeting The Exam Requirements
---
## Instructions to Run the Program

*Ensure you are in the root directory (`Rosla-Technology`) before running these commands.*

### Install the Dependencies
```bash
pip install -r flaskr/requirements.txt
```

### Run the Application
```bash
python flaskr/app.py
```
```bash
flask run
```

### Access the Application
Open your web browser and go to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Dependencies and System Requirements

See the `flaskr/requirements.txt` file for a full list of Python package dependencies. You will need Python 3.x installed.

# Asset Log for Libraries Used

## Python Libraries
- Flask: A micro web framework for Python.
  - Source: https://palletsprojects.com/p/flask/
  - License: BSD-3-Clause
- Werkzeug: A comprehensive WSGI web application library.
  - Source: https://palletsprojects.com/p/werkzeug/
  - License: BSD-3-Clause
- sqlite3: A lightweight, disk-based database library.
  - Source: https://docs.python.org/3/library/sqlite3.html
  - License: Python Software Foundation License

## JavaScript Libraries
- Chart.js: Simple yet flexible JavaScript charting library for the modern web
    - Soruce: https://www.chartjs.org/
    - License: MIT License

## CSS Libraries
- Google Fonts: Web fonts provided by Google.
  - Source: https://fonts.google.com/
  - License: Apache License, Version 2.0
- OpenDyslexic:  A typeface that uses typeface shapes & features to help offset some visual symptoms of Dyslexia. Now in SIL-OFL.
  - Source: https://github.com/antijingoist/opendyslexic 
  - License: SIL OPEN FONT LICENSE


## APIs
- Geoapify API: Used for geocoding and retrieving building geometry.
  - Source: https://www.geoapify.com/
- GetAddress.io API: Used for UK address autocompletion.
  - Source: https://getaddress.io/
- Google Gemini API: Used for processing text data (e.g., from OCR).
  - Source: https://ai.google.dev/
- OCR API: Used for extracting text from images/documents (Specific service not identified in code excerpts).


## Images
- `register.png`: Image used on login and registration pages
    - Soruce: Josh Hernandez
    - Licnese: All Rights Reserved - Replcae Imagie in production

- `solar.svg`: Solar panel icon used in solar consultation results
    - Soruce: Made My Self
    - Licence: None

- `index.png`: Main image for the homepage
    - Soruce: Josh Hernandez
    - Licnese: All Rights Reserved - Replcae Imagie in production

- `infoHub/reduceCFPIcon.svg`: Icon for the Reduce Carbon Footprint info page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/Arrow.svg`: Navigation arrow used across info page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/reduceCFP.svg`: Link image on the Info Hub page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/evChargers.svg`: Link image on the Info Hub page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/smartHome.svg`: Link image on the Info Hub page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/greenEnergy.svg`: Link image on the Info Hub page
    - Soruce: Made My Self
    - Licence: None

- `infoHub/title.svg`: Title graphic for the Info Hub page
    - Soruce: Made My Self
    - Licence: None

## Areas for Improvement

### Scalability
- **Limitation**: The application uses SQLite, which is suitable for development and small-scale applications but may not perform well under high traffic or with very large datasets due to its file-based nature and limited concurrency support.
- **Improvement**: Consider migrating to a more robust database system like PostgreSQL or MySQL for production environments.

### User Authentication
- **Limitation**: Current authentication relies on password hashing but lacks advanced security features such as multi-factor authentication (MFA), rate limiting, or account lockout mechanisms after multiple failed login attempts.
- **Improvement**: Implement MFA (e.g., using TOTP), add rate limiting to login attempts, and implement account lockouts to enhance security against brute-force attacks.

### Database Handling
- **Limitation**: Database connections and cursors are opened and closed within individual functions in `db.py`. This is repetitive and less efficient.
- **Improvement**: Centralise database connection management. Using Flask's application context (`g` object) or an Object-Relational Mapper (ORM) like SQLAlchemy can help manage connections more effectively and reduce code redundancy.
