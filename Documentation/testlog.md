# Testing Log for Coder Dojo Web Application

## Test Case 1: base.html

### Nav Bar Funcitonality
- Event
    - Click Nav Bar
- Expected Result: Redirect to next page
- Actual Result: Redirect to index
- Status: Fail
- Dependencies: None
- Fix: Fix Redirects Changing the HREFs To Be Acurate

- Event
    - Click Nav Bar
- Expected Result: Redirect to next page
- Actual Result: werkzeug.routing.BuildError werkzeug.routing.BuildError: Could not build url for endpoint 'infoHub'. Did you mean 'login' instead
- Status: Fail
- Fix: Add the routes to app.py

- Event
    - Click Nav Bar
- Expected Result: Redirect to next page
- Actual Result: Redirect to next page
- Status: Pass


## Test Case 2: User Registration

### UI/UX

- Event:
    - Click Register Field
- Expected Result: User can type in field
- Actual result: User cant click into the field
- Status: Fail
- Fix: Overlapping elements, Stoped using seperates divs for each filed

- Event:
    - Click Register Field
- Expected Result: User can type in field
- Actual result: User can type in field
- Status: Pass



### Normal Data
- Input: 
    - Email: user@example.com
    - Password: P@ssw0rd1234
    - Password2: P@ssw0rd1234
- Expected Result: User registered successfully.
- Actual Result: User registered successfully.
- Status: Pass
- Dependencies: User Database Table

### Erroneous Data
- Input: 
    - Email: user@example.com
    - Password: Password
    - Password2: Password
- Expected Result: Error Message saying that the password isn't strong enough.
- Actual Result: No visible error message to the user, just logged in the console.
- Status: Fail
- Fix: Configure Flask Flash
- Dependencies: User Database Table

- Input: 
    - Email: user@example.com
    - Password: Password
    - Password2: Password2
- Expected Result: Error Message saying that the passwords don't match.
- Actual Result: No visible error message to the user, just logged in the console.
- Status: Fail
- Fix: Configure Flask Flash
- Dependencies: User Database Table

### Boundary Data
- Input: 
    - Email: user@example.com
    - Password: P@ssw0rd123
    - Password2: P@ssw0rd123
- Expected Result: User registered successfully.
- Actual Result: User registered successfully.
- Status: Pass
- Dependencies: User Database Table

### Presence Check
- Input: 
    - Email: 
    - Password: 
    - Password2: 
- Expected Result: User registration stopped since fields are mandatory.
- Actual Result: User registration stopped.
- Status: Pass
- Dependencies: User Database Table

## Test Case 3: User Login

### UI/UX

- Event:
    - Click Register Field
- Expected Result: User can type in field
- Actual result: User cant click into the field
- Status: Fail
- Fix: Overlapping elements, Stoped using seperates divs for each filed

- Event:
    - Click Register Field
- Expected Result: User can type in field
- Actual result: User can type in field
- Status: Pass

### Normal Data
- Input: 
    - Email: user@example.com
    - Password: P@ssw0rd1234
- Expected Result: User signed in successfully.
- Actual Result: User not found.
- Status: Fail
- Fix: Add missing sqlite3 syntax to add_user function
- Dependencies: User Database Table + Registration

### Erroneous Data
- Input: 
    - Email: user@example.com
    - Password: Password
- Expected Result: Password incorrect.
- Actual Result: Flask Flash telling the user that their password is incorrect.
- Status: Pass
- Dependencies: User Database Table + Registration

### Boundary Data
- Input: 
    - Email: user@example.com (valid email format)
    - Password: P@ssw0 (just below the minimum password length, e.g., 7 characters)
- Expected Result: Password is incorrect.
- Actual Result: Flask Flash message indicating the password is incorrect and too short.
- Status: Pass
- Dependencies: User Database Table + Registration

### Presence Check
- Input: 
    - Email: (empty)
    - Password: P@ssw0rd1234
- Expected Result: System prompts the user to enter an email address.
- Actual Result: Flask Flash message indicating the email field is required.
- Status: Pass
- Dependencies: User Database Table + Registration

- Input: 
    - Email: user@example.com
    - Password: (empty)
- Expected Result: System prompts the user to enter a password.
- Actual Result: Flask Flash message indicating the password field is required.
- Status: Pass
- Dependencies: User Database Table + Registration

