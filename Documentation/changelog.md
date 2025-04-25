> ***Change Log***
> - **5389bbb** 2025-04-25 11:31:19 - Refactor booking deletion authorization logic, add footer links to index page, and update documentation
> - **f959b30** 2025-04-24 12:15:21 - Enhance user experience: implement cookie consent pop-up and set cookie functionality, improve layout and accessibility features.
> - **d14c608** 2025-04-24 12:03:33 - Enhance user dashboard: add account update section with password verification, email and password update fields, and improve layout for better user experience.
> - **077a465** 2025-04-24 11:25:16 - Enhance user dashboard: add installation requests table with delete functionality, improve layout and styling for better user experience.
> - **5343202** 2025-04-24 10:11:40 - Enhance admin dashboard: implement booking deletion functionality, add confirmation prompts, and improve layout for better user experience.
> - **4a279f9** 2025-04-23 15:12:22 - Enhance admin dashboard: add functionality to fetch and display installation requests and in-person assessment bookings, implement user role checks, and improve error handling.
> - **3cd4f87** 2025-04-23 14:51:49 - Enhance installation process: update form actions and fields, add booking time functionality, and implement database support for installation requests.
> - **183068b** 2025-04-23 12:20:27 - Enhance installation form: remove monthly bill input, add booking time field, and improve layout for better user experience.
> - **c740de5** 2025-04-23 10:50:15 - Enhance installation functionality: add form fields for address, solar and EV-specific data, implement form validation, and update template for improved user experience.
> - **1d58cba** 2025-04-23 10:02:36 - Enhance installation page: implement custom dropdown for product selection, add form fields for email and phone, and update styling for improved layout and accessibility.
> - **f64119c** 2025-04-22 15:14:17 - OpenDyslexic in assesiblity mode
> - **8535842** 2025-04-22 15:02:05 - Enhance accessibility and user feedback: update styling for accessibility icons, add error handling and success messages for booking functionality, and improve layout in various templates.
> - **3178721** 2025-04-22 13:20:03 - Enhance in-person consultation functionality: add booking feature with form validation and database integration; create new table for storing bookings
> - **8f14c7a** 2025-04-22 13:12:52 - Enhance registration functionality: generate a secure example password for users and update password hint in the registration template; fix security issue by suggesting randomly generated passwords
> - **21d5d94** 2025-04-22 12:56:08 - Enhance person consultation functionality: add form validation for name, phone, date, and time; implement phone number validation; update form action URL
> - **e25f383** 2025-04-22 12:39:24 - Enhance person consultation functionality: implement data retrieval from session, add error handling, and update template rendering
> - **186bbdd** 2025-04-03 12:16:38 - Enhance accessibility features: add styling for accessibility icons and improve hover effects in templates
> - **989dd36** 2025-04-03 12:11:47 - Enhance solar consultation functionality: retrieve and store user solar assessment data in session, improve error handling, and update results display + Added Assesbility button
> - **0eaf98a** 2025-04-03 10:25:11 - Refactor solar assessment functionality: delete existing assessment for user before inserting new entry
> - **698e1d9** 2025-04-03 10:22:40 - Add solar assessment functionality: create database table, implement data storage, and enhance solar consultation flow
> - **54d2876** 2025-04-02 15:10:38 - Enhance solar consultation functionality: add detailed test cases, improve error handling, and update results display in the template
> - **2e5cc1b** 2025-04-02 14:46:01 - Enhance solar consultation template: add property area information, adjust layout, and improve styling for better user experience
> - **dafa457** 2025-04-02 14:31:10 - Update changelog and testlog: add recent changes and improve test case documentation for geocoding functionality
> - **82101ab** 2025-04-02 10:16:32 - Update changelog and enhance solar consultation: improve address validation, update geocoding method, and refine error handling
> - **ccd5331** 2025-04-01 15:11:11 - Rename solar consultation route to solar assessment and add adress auto fill
> - **3f920d3** 2025-04-01 14:33:16 - Refactor solar consultation template: enhance layout, add postal code input, and improve address suggestions
> - **dc1e70f** 2025-04-01 13:12:20 - Update styles and templates for solar consultation: enhance layout and add new design elements
> - **ddac9b0** 2025-04-01 12:30:09 - Update changelog and testlog: enhance documentation for consultation module improvements and fix inaccuracies in test results
> - **2be0462** 2025-04-01 12:27:14 - Enhance consultation module: add error handling, logging, and solar potential calculation
> - **4b7a07b** 2025-04-01 11:32:32 - Refactor building area calculation to use Shapely and GeoPandas; update requirements and add dotenv support
> - **cbff7c5** 2025-04-01 10:43:48 - Refactor consultations.py to integrate improved API – Rip yesterday's work 😞
> - **e60f235** 2025-03-31 16:15:34 - Add consultation module for building area calculations: implement geocoding and Overpass API integration
> - **80a19a2** 2025-03-31 13:16:57 - Stable Completion of the energy tracker: Added file upload functionality with OCR processing; update requirements and .gitignore
> - **9815791** 2025-03-28 11:39:23 - Add file upload functionality and OCR processing; update requirements and .gitignore
> - **e5da77b** 2025-03-28 09:20:52 - Update styles and layout for InfoHub and smart home pages; enhance responsiveness and adjust changelog
> - **72d23f6** 2025-03-28 09:05:05 - Enhance user authentication by adding login checks to carbon footprint calculator route; update registration template with password hint and styling adjustments
> - **bc37f74** 2025-03-27 12:13:51 - Add error handling for various HTTP status codes and update changelog; adjust layout in carbon footprint calculator submission template
> - **ea3da93** 2025-03-27 11:56:11 - Add carbon footprint backend functionality and results template; update changelog and test log
> - **e5444d8** 2025-03-27 10:49:12 - Add changelog and update test log for Carbon Footprint Calculator UI
> - **24ad7bb** 2025-03-27 10:40:23 - Updated the carbon footprint calculater to have the complted form
> - **3132979** 2025-03-27 10:13:20 - Update test log for user login cases; add carbon footprint table and front end of the carbon footprint
> - **59cdc74** 2025-03-26 13:09:39 - Add flash message functionality for user authentication feedback
> - **508e222** 2025-03-26 12:45:26 - Finished Login and Register Front End input fields for email and password, social login buttons, and responsive design adjustments
> - **0d60d55** 2025-03-26 09:17:22 - Finish Info Pages
> - **258ba30** 2025-03-26 09:05:00 - rename energy tips route to reduce carbon footprint; update related HTML and SVG assets
> - **e4a64bf** 2025-03-25 15:12:03 - add new info section for carbon footprint reduction with interactive content and styles
> - **99d4eed** 2025-03-25 14:40:26 - update link colors in CFPI calculator and smart home templates
> - **354d54c** 2025-03-25 14:39:31 - add new SVG icon for CFPI calculator and update HTML template
> - **190112d** 2025-03-25 14:32:38 - refactor routing and templates for energy-related pages; add new info pages and improve image hover effects
> - **743e531** 2025-03-25 14:18:45 - update InfoHub template with new styles, image animations, and layout adjustments
> - **246037a** 2025-03-25 14:07:59 - add new routes for EV chargers, green energy, smart home, and energy tips; update InfoHub template with new links and images
> - **f10762b** 2025-03-25 12:38:37 - add logout route, update InfoHub and base templates, and add new SVG images
> - **85c1af5** 2025-03-25 12:14:03 - add routing for new pages and update navigation links in base template
> - **d3dd9c7** 2025-03-25 12:08:49 - add testing log for base.html functionality and create placeholder templates for various pages
> - **12b3a3c** 2025-03-25 12:01:52 - refactor layout and styles in base and index templates, add button styles and new sections
> - **00f982c** 2025-03-25 10:36:10 - add header and styling to base template, update index page, and create script file
> - **fb3f67a** 2025-03-25 10:10:31 - add initial Flask app structure with basic routing and templates
> - **aa0fedc** 2025-03-25 09:54:57 - initialize documentation and project structure