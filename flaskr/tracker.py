import os
import uuid
import easyocr
import dotenv
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import flash, redirect, url_for, request, session, current_app
from auth import get_user_id_by_email
from google import genai

#Load environment variables from .env file
dotenv.load_dotenv()
# Set up Google Gemini API client
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))


# Add these to your imports at the top
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Get user ID for file association
        user_id = get_user_id_by_email()
        if not user_id:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for('login'))
            
        # Generate unique filename to prevent collisions
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        
        # Create user-specific directory
        user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save the file
        filepath = os.path.join(user_upload_dir, unique_filename)
        file.save(filepath)
        
        return filepath  # Return the path where the file was saved
    
    return None  # Return None if file wasn't valid

def ocr_process_file(filepath):
    reader = easyocr.Reader(['en'])
    
    # Perform OCR on the image
    results = reader.readtext(filepath)
    
    # Extract text from results
    extracted_text = ""
    for detection in results:
        text = detection[1]  # The text is in the second position of each detection
        extracted_text += text + " "
        
        # Add newlines after periods to improve readability
        if text.endswith('.'):
            extracted_text += "\n"
    
    return extracted_text.strip()


print(ocr_process_file(r"C:\Users\16062\Downloads\assets_8ab3bbafae9e469c86ca663c018f53d4_76516ac34d9e4d6fabcf417854a9d748.webp"))
    
# Gemini data formating
def format_gemini(data):
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=f'''Summerise this electrsitcy bill in a table format with the following columns:
        "Date", "Description", "Amount", "Total Amount Due".'''
    )

    return(response.text)
