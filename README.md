# AIMedNow

AIMedNow is an AI-powered medical assistance application that provides intelligent responses to health-related queries and processes medical documents like doctor's notes.
<img width="889" alt="image" src="https://github.com/user-attachments/assets/72f077f9-fcc1-4b0f-b464-c250897c15a4" />

## Features

- **AI-Powered Health Assistance**: Ask medical questions and receive informative responses
- **Emergency Detection**: Automatic classification of emergency-related queries with appropriate warnings
- **Doctor's Note Translation**: Upload medical documents to get simplified, patient-friendly explanations
- **EHR Integration**: Previous medical document uploads are referenced when answering new questions
- **User-Friendly Interface**: Clean chat interface with light/dark mode support

## Technical Overview

AIMedNow is built using a Flask backend with a vanilla JavaScript frontend. The system leverages advanced AI models via the OpenAI API to process and respond to user queries.

### Key Components

1. **Flask Backend**:
   - Routes for handling text queries and image uploads
   - Emergency classification system
   - Doctor's note processing system

2. **Frontend**:
   - Responsive chat interface
   - File upload capabilities
   - Markdown rendering for formatted responses
   - Toggle for viewing original vs. simplified medical documents

3. **AI Systems**:
   - Question classification (emergency vs. non-emergency)
   - GraphRAG search for emergency-related questions
   - Medical document OCR and simplification
   - General health query responses

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- GraphRAG API key and models

### Environment Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   GRAPHRAG_API_KEY=
   MODEL_NAME=
   GRAPHRAG_LLM_MODEL=
   GRAPHRAG_EMBEDDING_MODEL=

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

python model_deployment.py
```

Access the application at http://localhost:5000

### Usage

#### Asking Health Questions
1. Type your health-related question in the chat box
2. If the question is classified as an emergency, you'll receive a response with medical guidance and an emergency notice
3. For general health questions, you'll receive informative answers

#### Uploading Medical Documents
1. Click the attachment icon in the chat interface
2. Select an image of a medical document or doctor's note
3. The system will analyze the document and provide:
   * A description of the document
   * For doctor's notes: both the original text and a simplified, patient-friendly version
4. Toggle between original and simplified views using the buttons provided

#### Reference Across Conversations
The system remembers previously uploaded medical documents and will reference them when relevant to new questions.

### Project Structure
* model_deployment.py - Main Flask application with routing and API integrations
* emergency_classifier.py - Logic for classifying and responding to emergency queries
* doctor_note_processor.py - Logic for processing and simplifying medical documents
* static/js/index.js - Frontend JavaScript for the chat interface
* static/css/style.css - Styling for the application
* templates/index.html - Main HTML template


License
This project is licensed under the MIT License - see the LICENSE file for details.

Disclaimer
AIMedNow is designed to provide general health information and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
```


