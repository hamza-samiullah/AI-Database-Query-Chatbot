from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import json
import requests
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from contextlib import asynccontextmanager
from seed_data import seed_database

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Global database connection
db_conn = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create in-memory DB and seed it
    global db_conn
    try:
        logger.info("Starting up: Creating in-memory database...")
        db_conn = sqlite3.connect(":memory:", check_same_thread=False)
        seed_database(db_conn)
        logger.info("Database seeded successfully.")
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        # We don't crash here so the health check can still pass for debugging
    
    yield
    
    # Shutdown
    if db_conn:
        db_conn.close()
        logger.info("Database connection closed.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY is not set!")

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "z-ai/glm-4.5-air:free")

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    answer: str
    sql: str
    data: Optional[List[Dict[str, Any]]] = None
    visualization_type: Optional[str] = None

def get_db_schema():
    cursor = db_conn.cursor()
    
    schema = ""
    tables = ["customers", "products", "orders", "order_items"]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        schema += f"Table: {table}\nColumns: {', '.join(column_names)}\n\n"
        
    return schema


from datetime import datetime

def execute_sql(sql_query):
    try:
        cursor = db_conn.cursor()
        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        
        # Convert to list of dicts
        results = []
        for row in data:
            results.append(dict(zip(columns, row)))
            
        return results, columns
    except Exception as e:
        return str(e), []

import time

def generate_sql_and_answer(query: str, history: List[Dict[str, str]]):
    schema = get_db_schema()
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    system_prompt = f"""You are an expert data analyst. You have access to a SQLite database with the following schema:

{schema}

Your goal is to answer the user's question by generating a valid SQL query.
Return the SQL query inside a JSON object.
Format:
{{
  "sql": "SELECT ...",
  "explanation": "Brief explanation of what the query does"
}}

Rules:
1. Use only SQLite syntax.
2. The current date is {current_date}.
3. Return ONLY the JSON object. Do not wrap it in markdown code blocks.
"""

    messages = [{"role": "system", "content": system_prompt}]
    # Add history slightly modified to fit context if needed, but for simplicity just last few
    for msg in history[-5:]: 
        messages.append(msg)
    
    messages.append({"role": "user", "content": query})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173", # Update to match frontend
        "X-Title": "LightChatbot"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Sending request to OpenRouter (Attempt {attempt+1}/{max_retries})...")
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=30 # Add timeout
            )
            
            if response.status_code == 429:
                print("Rate limited. Retrying...")
                time.sleep(2 * (attempt + 1)) # Exponential backoff
                continue
                
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            print(f"AI Response: {content}")
            
            # Cleanup if markdown is present (common issue with LLMs)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                # Fallback if no JSON
                return {"sql": "", "explanation": content}
                
        except requests.exceptions.Timeout:
            print("Request timed out.")
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
        
        time.sleep(1)

    return {"sql": "", "explanation": "The AI service is currently busy or experiencing high traffic (429 Rate Limit). Please try again in a moment."}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ai_response = generate_sql_and_answer(request.message, request.history)
    
    sql_query = ai_response.get("sql", "")
    explanation = ai_response.get("explanation", "")
    
    data_list = []
    viz_type = "table"

    if sql_query:
        result, columns = execute_sql(sql_query)
        if isinstance(result, list):
            # Limit results for frontend performance
            if len(result) > 100:
                result = result[:100]
            
            data_list = result
            
            # Simple heuristic for visualization
            if len(data_list) > 0:
                 # Check if we have 2 columns and the second one is likely numeric
                if len(columns) == 2:
                     first_val = data_list[0][columns[1]]
                     if isinstance(first_val, (int, float)):
                        viz_type = "bar"
                     
                if "date" in columns[0].lower() or "time" in columns[0].lower():
                   viz_type = "line"
        else:
            explanation += f"\nError executing SQL: {result}"
    
    return ChatResponse(
        answer=explanation,
        sql=sql_query,
        data=data_list,
        visualization_type=viz_type
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

# To run: uvicorn main:app --reload
