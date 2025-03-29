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
load_dotenv()
client = OpenAI(base_url=os.getenv("API_URL"), api_key=os.getenv("API_KEY"))
UPLOAD_FOLDER = './upload_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def get_answer2question(question):
    print("Got question: ", question)
    completion = client.chat.completions.create(
                model="qwen2-vl",
                messages=[
                    {'role': 'system', 'content': 'You are an expert in answering questions based on the provided context.'},
                    {'role': 'system', 'content': question}
                ],
                temperature=0.8
    )
    print("Got completion")
    return completion.choices[0].message.content
def encode_image(image_path):
    # from https://community.openai.com/t/how-to-load-a-local-image-to-gpt4-vision-using-api/533090/3
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
def get_answer2question_from_image(base64_image, question, extra_body, temperature=0.5):
    chat_response = client.chat.completions.create(
        model="qwen2-vl",
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
    return chat_response.choices[0].message.content

app = Flask(__name__)
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
            answer = get_answer2question_from_image(encode_image(filepath), "Describe everything medically important in the image.")
            return jsonify({'answer': answer})
    # For referencing this flask server in the frontend, use a action="http://..../api/predict_tb" in the form
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
        response = get_answer2question(question)
        print("Response is ", response)
        return jsonify({'answer': response}), 200
    
    except Exception as e:
        print("got error", e)
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, static_files={'/static': './generated/'})
