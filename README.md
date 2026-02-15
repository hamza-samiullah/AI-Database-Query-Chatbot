# Light AI Chatbot

A lightweight conversational AI chatbot that allows users to query a local SQLite database using natural language. Built with FastAPI, React, and Groq (Llama 3.3).

## Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Groq API Key

## Setup & Running

### 1. Backend

 Navigate to the backend directory:
 ```bash
 cd backend
 ```

 Create a virtual environment and install dependencies:
 ```bash
 python -m venv venv
 source venv/bin/activate  # On Windows: venv\\Scripts\\activate
 pip install -r requirements.txt
 ```

 Configure `.env`:
 ```bash
 GROQ_API_KEY=your_groq_api_key
 ```

 Seed the database (optional, happens on startup):
 ```bash
 python seed_data.py
 ```

 Start the server:
 ```bash
 uvicorn main:app --reload --port 8000
 ```
 The API will be available at `http://localhost:8000`.

### 2. Frontend

 Open a new terminal and navigate to the frontend directory:
 ```bash
 cd frontend
 ```

 Install dependencies:
 ```bash
 npm install
 ```

 Start the development server:
 ```bash
 npm run dev
 ```
 Open your browser at `http://localhost:5173` (or the port shown in terminal).

## Usage
1. Type a question in the chat, e.g., "Show me top 5 customers" or "Total sales by category".
2. The AI will generate a SQL query using **Llama 3.3**, execute it, and display the results in a table or chart.
