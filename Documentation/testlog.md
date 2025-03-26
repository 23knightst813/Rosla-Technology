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

## Test Case 3: User Registration

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

