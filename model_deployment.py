import io
import json
from PIL import Image
from flask import Flask, jsonify, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
import base64
from openai import OpenAI
from flask_cors import CORS
import os
from dotenv import load_dotenv
from emergency_classifier import process_question_sync
from doctor_note_processor import process_doctor_note

load_dotenv()

client = OpenAI(api_key=os.getenv("GRAPHRAG_API_KEY"))

client_model = "gpt-4o"  #"qwen2-vl"

UPLOAD_FOLDER = './upload_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def encode_image(image_path):
    # from https://community.openai.com/t/how-to-load-a-local-image-to-gpt4-vision-using-api/533090/3
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_answer2question_from_image(base64_image, question, extra_body=None, temperature=0.5):

    chat_response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "You're a helpful agent."}
                ]
            },
            {
                "role": "user",
                "content": [
                    # NOTE: The prompt formatting with the image token `<image>` is not needed
                    # since the prompt will be processed automatically by the API server.
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
        temperature=temperature,
        extra_body=extra_body
    )
    print(chat_response)
    return chat_response.choices[0].message.content

# app = Flask(__name__)
app = Flask(__name__, static_folder='static', static_url_path='/static')

CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload_ehr', methods=['POST', 'GET'])
def upload_ehr():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get base64 encoded image
            base64_image = encode_image(filepath)
            
            # First get a general description of the image
            initial_description = get_answer2question_from_image(
                base64_image, 
                "Describe in 100 words or less what is in the image."
            )
            
            # Check if the image is a doctor's note and process it if it is
            doc_note_result = process_doctor_note(base64_image, initial_description)
            
            # If it's a doctor's note, return the processed information
            if doc_note_result.get("is_doctor_note", False):
                response = {
                    'answer': initial_description,
                    'is_doctor_note': True,
                    'original_text': doc_note_result["original_text"],
                    'simplified_text': doc_note_result["simplified_text"]
                }
            else:
                # If it's not a doctor's note, just return the initial description
                response = {
                    'answer': initial_description,
                    'is_doctor_note': False
                }
            
            file.close()
            os.remove(filepath)
            return jsonify(response)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/api/qna', methods=['POST'])
def qna():
    data = request.get_json()
    question = data.get('text')

    #Replace the double quotes
    question = question.replace('"','')

    if not question:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Process the question using our fixed emergency classification system
        response_data = process_question_sync(question)
        
        # Add the classification info to the response for the frontend to use if needed
        response = {
            'answer': response_data['answer'],
            'classification': response_data['classification'],
            'source': response_data['source']
        }
        
        print(f"Response classification: {response['classification']}, source: {response['source']}")
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in qna route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'answer': "I'm sorry, I encountered an error processing your question."}), 500


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure required environment variables are set
    required_vars = ["GRAPHRAG_API_KEY", "MODEL_NAME", "GRAPHRAG_LLM_MODEL", "GRAPHRAG_EMBEDDING_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Set these in your .env file for proper functionality.")
    
    # Install nest_asyncio for handling nested event loops
    try:
        import nest_asyncio
        nest_asyncio.apply()
        print("Applied nest_asyncio for handling nested event loops")
    except ImportError:
        print("Warning: nest_asyncio not installed. This may cause issues with async operations.")
        print("Install with: pip install nest_asyncio")

    app.run(debug=True)