# AIMedNow

AIMedNow is an AI-powered medical assistance application that provides intelligent responses to health-related queries and processes medical documents like doctor's notes.

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