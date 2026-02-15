# Light AI Chatbot

A lightweight conversational AI chatbot that allows users to query a local SQLite database using natural language. Built with FastAPI, React, and OpenRouter (GLM-4.5).

## Prerequisites
- Node.js (v18+)
- Python (v3.10+)

## Setup & Running

### 1. Backend

 Navigate to the backend directory:
 ```bash
 cd backend
 ```

 Create a virtual environment and install dependencies:
 ```bash
 python -m venv venv
 source venv/bin/activate  # On Windows: venv\Scripts\activate
 pip install -r requirements.txt
 ```

 Seed the database (creates `retail.db`):
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
2. The AI will generate a SQL query, execute it, and display the results in a table or chart.
