# Testing Log

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

## Test Case 4: Carbon Footprint Calculator UI

### Display Elements
- Event:
    - Navigate to Carbon Footprint Calculator page
- Expected Result: All elements (title, options, chart, progress bar) displayed correctly
- Actual Result: Elements displayed correctly
- Status: Pass
- Dependencies: None

### Responsive Layout
- Event:
    - View calculator on mobile device
- Expected Result: Layout adjusts to fit screen size
- Actual Result: Chart overlaps with form on small screens
- Status: Fail
- Fix: Add media queries for smaller screens
- Dependencies: None

- Event:
    - View calculator on mobile device after fix
- Expected Result: Layout adjusts to fit screen size
- Actual Result: Layout adjusts correctly
- Status: Pass
- Dependencies: None


### Next Button Functionality
- Event:
    - Click Next without selecting an option
- Expected Result: Next button disabled, cannot proceed
- Actual Result: Next button disabled as expected
- Status: Pass
- Dependencies: None

- Event:
    - Select option then click Next
- Expected Result: Move to next step, progress bar updates
- Actual Result: Moved to next step, but progress bar disappeared
- Status: Fail
- Fix: Maintain progress bar state between steps
- Dependencies: None

- Event:
    - Select option then click Next after fix
- Expected Result: Move to next step, progress bar maintains progress
- Actual Result: Step navigation and progress bar work correctly
- Status: Pass
- Dependencies: None

### Back Button Functionality
- Event:
    - Click Back button on step 2
- Expected Result: Return to step 1, maintain selection
- Actual Result: Returned to step 1, but previous selection not highlighted
- Status: Fail
- Fix: Preserve selected state when navigating back
- Dependencies: None

- Event:
    - Click Back button on step 2 after fix
- Expected Result: Return to step 1, maintain selection
- Actual Result: Previous selection maintained correctly
- Status: Pass
- Dependencies: None


### Visual Feedback
- Event:
    - Click on an option
- Expected Result: Option becomes highlighted/selected
- Actual Result: Option becomes highlighted with darker color
- Status: Pass
- Dependencies: None

### Multiple Selections
- Event:
    - Select one option then select another in same step
- Expected Result: First selection deselected, new selection highlighted
- Actual Result: Behaves as expected
- Status: Pass
- Dependencies: None

### Data Storage
- Event:
    - Select options across multiple steps
- Expected Result: All selections stored in form data
- Actual Result: Data stored correctly in hidden inputs
- Status: Pass
- Dependencies: None


### Progress Bar Initial State
- Event:
    - Load calculator page
- Expected Result: Empty progress bar (0% filled)
- Actual Result: Progress bar showing partial fill before any selection
- Status: Fail
- Fix: Initialize progress bar to empty state
- Dependencies: None

### Progress Bar Step Progression
- Event:
    - Complete all 4 steps
- Expected Result: Progress bar fills incrementally (25%, 50%, 75%, 100%)
- Actual Result: Progress bar jumps to 100% after step 4
- Status: Fail
- Fix: Adjust progress fill path calculation
- Dependencies: None

- Event:
    - Complete all 4 steps after fix
- Expected Result: Progress bar fills incrementally
- Actual Result: Progress bar fills as expected
- Status: Pass
- Dependencies: None

### Progress Bar State Persistence
- Event:
    - Complete step 1, go to step 2, then back to step 1
- Expected Result: Progress bar maintains 25% fill
- Actual Result: Progress bar resets to 0%
- Status: Fail
- Fix: Maintain highest completed step in state
- Dependencies: None

- Event:
    - Complete step 1, go to step 2, then back to step 1 after fix
- Expected Result: Progress bar maintains 25% fill
- Actual Result: Progress bar maintains correct fill level
- Status: Pass
- Dependencies: None

### Chart Initial Display
- Event:
    - Load calculator page
- Expected Result: Chart displayed with default values
- Actual Result: Chart displayed correctly
- Status: Pass
- Dependencies: Chart.js

### Chart Updates
- Event:
    - Select different options
- Expected Result: Chart segments update to reflect selections
- Actual Result: Chart not updating when selections change
- Status: Fail
- Fix: Add chart.update() call after data changes
- Dependencies: Chart.js

- Event:
    - Select different options after fix
- Expected Result: Chart segments update to reflect selections
- Actual Result: Chart updates correctly
- Status: Pass
- Dependencies: Chart.js

## Test Case 5: Carbon Footprint Calculation & Submission


### Authentication Check
- Event:
    - Submit form while not logged in
- Expected Result: Redirect to login page with error message
- Actual Result: Redirected to login page with "You must be logged in" flash message
- Status: Pass
- Dependencies: Session management

### Calculation Logic
- Event:
    - Submit form with Carnivore diet, Car transport, High energy usage, No recycling
- Expected Result: Total emissions calculated correctly (3.0 + 2.5 + 3.5 + 0.5 = 9.5 tonnes)
- Actual Result: Total emissions calculated as 9.5 tonnes
- Status: Pass
- Dependencies: None

- Event:
    - Submit form with other diet, public transport, Medium energy usage, Recycling
- Expected Result: Total emissions calculated correctly (2.0 + 1.5 + 2.0 + 0.2 = 5.7 tonnes)
- Actual Result: Total emissions calculated as 5.7 tonnes
- Status: Pass
- Dependencies: None

### Database Storage
- Event:
    - Submit form with valid data while logged in
- Expected Result: Carbon footprint entry saved to database
- Actual Result: Entry saved with correct user ID, date, and calculated values
- Status: Pass
- Dependencies: Database connection, User authentication

### Error Handling
- Event:
    - Submit form with valid data but database connection fails
- Expected Result: User shown error message and redirected to calculator
- Actual Result: "Error adding carbon footprint entry" flash message and redirect to calculator
- Status: Pass
- Dependencies: Database error simulation

### Form Validation
- Event:
    - Submit form with missing transport value
- Expected Result: System uses default value for calculation
- Actual Result: Default transport emissions of 1.5 tonnes used
- Status: Pass
- Dependencies: None

### Redirect Logic
- Event:
    - Access page via GET request
- Expected Result: Redirect to calculator page
- Actual Result: Redirected to calculator page
- Status: Pass
- Dependencies: None

### Template Rendering
- Event:
    - Submit valid form with all values
- Expected Result: Results template rendered with all submitted values
- Actual Result: cfp_calculator_submit.html rendered with diet, transport, energy, waste, and total_emissions
- Status: Pass
- Dependencies: Template existence

## Test Case 5: Energy Tracker

- Event
    - User Upload File
- Expected Result: File can then be proccesed by the server
- Actual Result: Since the file was just saved as the file name, theres no identifcation to the user
- Status: Fail
- Fix: Generate unique filename and  Create user-specific directorys
- Dependencies: Tracker Font End

- Event
    - User Upload File
- Expected Result: File can then be proccesed by the server
- Actual Result:  File can then be proccesed by the server
- Status: Pass
- Dependencies: Tracker Font End
- Event:
    - Use OCR to extract text from the electricity bill
- Expected Result: Text returned
- Actual Result: Text was returned but it was very slow
- Status: Fail
- Fix: Switch from doctr to easyocr

- Event:
    - Use OCR to extract text from the electricity bill
- Expected Result: Text returned
- Actual Result: Text was returned quicker but still slow
- Status: fail
- Fix: User a api instead of running the ocr prediction locally

- Event:
    - Use OCR API to extract text from the electricity bill
- Expected Result: Text returned
- Actual Result: Text was quickly - 0.57 seconds
- Status: Pass


- Event:
    - Load the page and attempt to upload a file
- Expected Result: User can press the button pick a file and sumbit it
- Actual Resukt: Button was unclickable and in the wrong location 
- Status: Fail
- Fix: Move the button into the correct place

- Event:
    - Load the page and attempt to upload a file
- Expected Result: User can press the button pick a file and sumbit it
- Actual Result: Button was unclickable
- Status: Fail
- Fix: Switch the button form a label into a normal button element

- Event:
    - Load the page and attempt to upload a file
- Expected Result: User can press the button pick a file and sumbit it, and the data is processed and returned
- Actual Result: User can press the button pick a file and sumbit it, but the data is not processed correctly
- Status: Fail
- Fix: Use a smarter AI Model


- Event:
    - Load the page and attempt to upload a file
- Expected Result: User can press the button to pick a file, submit it, and have the data processed and returned.
- Actual Result: User can press the button to pick a file and submit it, but the data is processed correctly.
- Status: Needs Improvement
- Conclusion: While using a more advanced AI model resolves the issue, it is not cost-effective for the project and exceeds the limits of the free tier. Instead, efforts will focus on refining the prompt to improve performance within the current constraints.

## Test Case 6: Online Solar Consultation

- Event:
    - Use the Geocoding function to get coordinates form a adress
- Expected Result: Returns Vaild Cords
- Actual Result: Returns Vaild Cords
- Status: Pass

- Event:
    - Use use the fetch_raw_building_data to get all the cords form buildings around the coordinates
- Expected Result: Retuns a long list of cords what are relevant
- Actual Result:  Retuns a long list of cords what are not relevant, and in the middle of the see
- Status: Fail
- Fix: I accedently fed the latitudie into the logn and visa versa, so dstop doign that

- Event:
    - Use use the fetch_raw_building_data to get all the cords form buildings around the coordinates
- Expected Result: Retuns a long list of cords what are relevant
- Actual Result: Retuns a long list of cords what are relevant
- Status: Pass

- Event:
    - Use use the  get_building_cords to get all the cords form from the specifc house
- Expected Result: Retuns a short list of cords what are of the house
- Actual Result:  Retuns a short list of cords what are of the house
- Status: Pass

- Event:
    - Use use the  get_building_cords to get all the cords form from the specifc house
- Expected Result: Retuns a short list of cords what are of the house
- Actual Result:  Retuns a short list of cords what are of the house
- Status: Pass

- Event:
    - Calculate the are of the house with building_area
- Expected Result: Retuns the area
- Actual Result: Retuns the area but its very inacuate
- Status: Fail
- Fix: Use the shapely libary isntead

- Event:
    - Calculate the are of the house with building_area
- Expected Result: Retuns the area
- Actual Result: Retuns the are
- Status: Pass

- Event:
    - Calculate the the direction of the building using calculate_orientation
- Expected Result: Retuns the direction
- Actual Result: Retuns the direction
- Status: Pass

- Event:
    - Calculate soalr pannel infoamtion using  solar_potential
- Expected Result: Retuns the "area","orientation","usable_area","energy_potential","pannel_count","price_estimate","monthly_payment","energy_savings"
- Actual Result: Retuns the "area","orientation","usable_area","energy_potential","pannel_count","price_estimate","monthly_payment","energy_savings"
- Status: Pass