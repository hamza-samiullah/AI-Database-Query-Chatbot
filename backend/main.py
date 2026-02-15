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


import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


import random
from datetime import datetime, timedelta

def seed_database_internal(conn):
    cursor = conn.cursor()
    
    # Tables
    cursor.execute(""" CREATE TABLE IF NOT EXISTS customers (
                        id integer PRIMARY KEY,
                        name text NOT NULL,
                        email text,
                        city text,
                        signup_date text
                    ); """)

    cursor.execute(""" CREATE TABLE IF NOT EXISTS products (
                        id integer PRIMARY KEY,
                        name text NOT NULL,
                        category text,
                        price real
                    ); """)

    cursor.execute(""" CREATE TABLE IF NOT EXISTS orders (
                        id integer PRIMARY KEY,
                        customer_id integer NOT NULL,
                        order_date text,
                        total_amount real,
                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                    ); """)

    cursor.execute(""" CREATE TABLE IF NOT EXISTS order_items (
                        id integer PRIMARY KEY,
                        order_id integer NOT NULL,
                        product_id integer NOT NULL,
                        quantity integer,
                        price_at_purchase real,
                        FOREIGN KEY (order_id) REFERENCES orders (id),
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    ); """)

    # Seed Data (Check if exists first)
    cursor.execute("SELECT count(*) FROM customers")
    if cursor.fetchone()[0] > 0:
        return

    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    for i in range(1, 101):
        name = f"Customer {i}"
        email = f"customer{i}@example.com"
        city = random.choice(cities)
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)", (name, email, city, date))

    categories = ["Electronics", "Clothing", "Home", "Books"]
    for i in range(1, 21):
        name = f"Product {i}"
        category = random.choice(categories)
        price = round(random.uniform(10.0, 500.0), 2)
        cursor.execute("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", (name, category, price))

    for i in range(1, 201):
        customer_id = random.randint(1, 100)
        order_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)", (customer_id, order_date, 0))
        order_id = cursor.lastrowid

        total_amount = 0
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            product_id = random.randint(1, 20)
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            price = cursor.fetchone()[0]
            quantity = random.randint(1, 3)
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)", (order_id, product_id, quantity, price))
            total_amount += price * quantity
        
        cursor.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (total_amount, order_id))

    conn.commit()

def get_db_connection():
    try:
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        seed_database_internal(conn)
        return conn
    except Exception as e:
        logger.error(f"Failed to create DB connection: {e}")
        return None


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY is not set!")

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    answer: str
    sql: str
    data: Optional[List[Dict[str, Any]]] = None
    visualization_type: Optional[str] = None

def get_db_schema():
    conn = get_db_connection()
    if not conn:
        return "Error connecting to database."
        
    cursor = conn.cursor()
    
    schema = ""
    tables = ["customers", "products", "orders", "order_items"]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        schema += f"Table: {table}\nColumns: {', '.join(column_names)}\n\n"
    
    conn.close()
    return schema


from datetime import datetime

def execute_sql(sql_query):
    conn = get_db_connection()
    if not conn:
        return "Error connecting to database.", []

    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        
        # Convert to list of dicts
        results = []
        for row in data:
            results.append(dict(zip(columns, row)))
            
        conn.close()
        return results, columns
    except Exception as e:
        if conn:
            conn.close()
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
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Sending request to Groq (Attempt {attempt+1}/{max_retries})...")
            response = requests.post(
                f"{GROQ_BASE_URL}/chat/completions", 
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
