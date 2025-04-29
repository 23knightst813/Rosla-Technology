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
