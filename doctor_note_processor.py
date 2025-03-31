import base64
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("GRAPHRAG_API_KEY"))

def is_doctor_note(image_description):
    """
    Determine if the uploaded image is a doctor's note based on its description.
    
    Args:
        image_description (str): The description of the image from initial VLM analysis
        
    Returns:
        bool: True if the image is likely a doctor's note, False otherwise
    """
    prompt = f"""
    Based on this image description, determine if this is a doctor's note, medical prescription, 
    or other clinical documentation. Consider keywords like "prescription", "diagnosis", 
    "treatment plan", "medical terminology", etc.
    
    Description: {image_description}
    
    Answer only with "YES" if it's a doctor's note or medical document, or "NO" if it's not.
    """
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4"),
        messages=[
            {"role": "system", "content": "You are an AI that identifies medical documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=10
    )
    
    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"

def ocr_doctor_note(base64_image):
    """
    Perform OCR on a doctor's note image using a vision model.
    
    Args:
        base64_image (str): Base64 encoded image
        
    Returns:
        str: Extracted text from the image
    """
    prompt = """
    This image contains a doctor's note or medical documentation.
    Please carefully extract ALL text from this image, preserving the exact medical terminology.
    Include all sections, headings, medications, dosages, instructions, and any handwritten text.
    Try to maintain the original layout structure when possible.
    """
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4"),
        messages=[
            {
                "role": "system",
                "content": "You are an OCR system specialized in medical documentation. Extract all text faithfully."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
        temperature=0.1,
        max_tokens=1500
    )
    
    return response.choices[0].message.content

def simplify_medical_text(medical_text):
    """
    Simplify medical text to a 7th-grade reading level, add definitions,
    and provide clear instructions.
    
    Args:
        medical_text (str): The extracted text from the doctor's note
        
    Returns:
        dict: A dictionary containing simplified text and the original text
    """
    prompt = f"""
    Below is text extracted from a doctor's note or prescription. Please:
    
    1. Rewrite this at a 7th-grade reading level (age 12-13) while preserving all important medical information
    2. For each medical jargon term, add a brief, simple definition in [brackets]
    3. Convert any treatment instructions into clear, step-by-step directions 
    4. Organize information into sections: Diagnosis, Medications, Instructions, and Follow-up
    5. If there are medications, clearly explain: what each is for, how to take it, and potential side effects to watch for
    6. In the last paragraph provide a paragraph summarizing what the report says in an 8th-grade level and patient-friendly manner.
    
    Original text:
    {medical_text}
    """
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4"),
        messages=[
            {
                "role": "system",
                "content": "You are a medical translator who makes complex medical information accessible to the general public."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return {
        "original": medical_text,
        "simplified": response.choices[0].message.content
    }

def process_doctor_note(base64_image, initial_description):
    """
    Process a doctor's note image: check if it's a doctor's note,
    perform OCR, and simplify the content.
    
    Args:
        base64_image (str): Base64 encoded image
        initial_description (str): Initial description from the VLM
        
    Returns:
        dict: Processing results including simplified content and original
    """
    # Check if it's a doctor's note
    if not is_doctor_note(initial_description):
        return {
            "is_doctor_note": False,
            "message": "This doesn't appear to be a doctor's note or medical document."
        }
    
    # Perform OCR on the image
    extracted_text = ocr_doctor_note(base64_image)
    
    # Simplify the medical text
    processed_content = simplify_medical_text(extracted_text)
    
    return {
        "is_doctor_note": True,
        "original_text": processed_content["original"],
        "simplified_text": processed_content["simplified"]
    }