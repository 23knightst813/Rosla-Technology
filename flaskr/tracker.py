import os
import uuid
import dotenv
import requests
import logging
from werkzeug.utils import secure_filename
from flask import flash, redirect, url_for, current_app
from auth import get_user_id_by_email
from google import genai
import json

#Load environment variables from .env file
dotenv.load_dotenv()
# Set up Google Gemini API client
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Add these to your imports at the top
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    is_allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if not is_allowed:
        logger.warning(f"File rejected: {filename} - type not allowed")
    return is_allowed


def save_uploaded_file(file):
    logger.info(f"Processing file upload: {file.filename if file else 'None'}")
    
    if file and allowed_file(file.filename):
        # Get user ID for file association
        user_id = get_user_id_by_email()
        if not user_id:
            logger.error("File upload failed: User not found or not logged in")
            flash("User not found. Please log in again.", "error")
            return redirect(url_for('login'))
            
        # Generate unique filename to prevent collisions
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Create user-specific directory
        user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_upload_dir, exist_ok=True)
        logger.debug(f"Created or confirmed upload directory: {user_upload_dir}")
        
        # Save the file
        filepath = os.path.join(user_upload_dir, unique_filename)
        file.save(filepath)
        logger.info(f"File saved successfully: {filepath} for user {user_id}")
        
        return filepath  # Return the path where the file was saved
    
    logger.warning(f"Invalid file upload attempt: {file.filename if file else 'None'}")
    return None  # Return None if file wasn't valid



def ocr_process_file(filename):
    logger.info(f"Processing file for OCR: {filename}")
    """Process an image file using OCR.space API for faster performance."""
    api_key = os.getenv('OCR_SPACE_API_KEY')
    
    if not api_key:
        logger.error("OCR_SPACE_API_KEY environment variable is not set")
        return "OCR API key not configured"
        
    payload = {'isOverlayRequired': False,
            'apikey': api_key,
            'language': 'eng',
            }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                        files={filename: f},
                        data=payload,
                        )
    logger.debug(f"OCR response done")
    return r.content.decode()
            
    
    
# Process data using Gemini API
def gemini_format(data):
    logger.info("Sending data to Gemini API for formatting")
    contents = f"""Use this format to structure the data {data}, dont return ```json, just return the json object. 
    Make sure billing period dates are in YYYY-MM-DD format. If you can't extract a precise date, use the first day of the month for start date and last day of the month for end date:
                    {{
                        "billingPeriod": {{
                            "startDate": "YYYY-MM-DD",
                            "endDate": "YYYY-MM-DD"
                        }},
                        "usageTotalsFromBill": {{ 
                            "electricityCostGBP": 0.00,
                            "gasCostGBP": 0.00
                        }}
                    }}
            """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=contents
        )
        response_text = response.text.strip()

        # Remove markdown formatting if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()  

        # Parse JSON 
        try:
            response_data = json.loads(response_text)
            
            # Validate the date formats
            if isinstance(response_data, dict):
                billing_period = response_data.get('billingPeriod', {})
                start_date = billing_period.get('startDate', '')
                end_date = billing_period.get('endDate', '')
                
                # Use a default format if date is missing or malformed
                import datetime
                try:
                    if not start_date or len(start_date) < 10:
                        billing_period['startDate'] = datetime.datetime.now().strftime("%Y-%m-01")
                        logger.warning("Missing start date, using default")
                    else:
                        # Validate date format
                        datetime.datetime.strptime(start_date, "%Y-%m-%d")
                        
                    if not end_date or len(end_date) < 10:
                        today = datetime.datetime.now()
                        last_day = datetime.date(today.year, today.month, 1) + datetime.timedelta(days=32)
                        last_day = last_day.replace(day=1) - datetime.timedelta(days=1)
                        billing_period['endDate'] = last_day.strftime("%Y-%m-%d")
                        logger.warning("Missing end date, using default")
                    else:
                        # Validate date format
                        datetime.datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    # Invalid date format, use defaults
                    logger.warning("Invalid date format detected, using default dates")
                    today = datetime.datetime.now()
                    billing_period['startDate'] = today.strftime("%Y-%m-01")
                    last_day = datetime.date(today.year, today.month, 1) + datetime.timedelta(days=32)
                    last_day = last_day.replace(day=1) - datetime.timedelta(days=1)
                    billing_period['endDate'] = last_day.strftime("%Y-%m-%d")
                    
                # Ensure we have numeric values for costs
                usage_totals = response_data.get('usageTotalsFromBill', {})
                if not isinstance(usage_totals.get('electricityCostGBP'), (int, float)):
                    usage_totals['electricityCostGBP'] = 0.0
                if not isinstance(usage_totals.get('gasCostGBP'), (int, float)):
                    usage_totals['gasCostGBP'] = 0.0
                
            # Convert to list if needed
            if isinstance(response_data, dict):
                response_data = [response_data]
                
            return response_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            # Return a default empty but valid data structure
            return [{"billingPeriod": {"startDate": datetime.datetime.now().strftime("%Y-%m-01"), 
                                      "endDate": datetime.datetime.now().strftime("%Y-%m-%d")},
                    "usageTotalsFromBill": {"electricityCostGBP": 0.0, "gasCostGBP": 0.0}}]

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        # Return a default empty but valid data structure with today's date
        import datetime
        return [{"billingPeriod": {"startDate": datetime.datetime.now().strftime("%Y-%m-01"), 
                                  "endDate": datetime.datetime.now().strftime("%Y-%m-%d")},
                "usageTotalsFromBill": {"electricityCostGBP": 0.0, "gasCostGBP": 0.0}}]




if __name__ == "__main__":
    logger.info("Running OCR and formatting test")
    # test_result = gemini_format(print(ocr_process_file(r"C:\Users\16062\Downloads\assets_8ab3bbafae9e469c86ca663c018f53d4_76516ac34d9e4d6fabcf417854a9d748 (1).png")))
    test_result = ocr_process_file(r"C:\Users\16062\Downloads\octo.png")
    print(test_result)
