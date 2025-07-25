from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import csv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load examples.csv to get example prompts and responses
def load_examples():
    try:
        examples_text = "EXAMPLES:\n"
        count = 0
        with open('examples.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip() and count < 3:
                    examples_text += f"Q: {row[0]}\nA: {row[1]}\n"
                    count += 1
        
        return examples_text
    except Exception as e:
        return f"Error loading examples: {str(e)}\n"

# Load indicators.csv to get database schema
def load_database_schema():
    try:
        schema_description = "TABLES:\n"
        tables = {}
        
        with open('indicators.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                table = row['table']
                if table not in tables:
                    tables[table] = []
                tables[table].append(f"{row['column']} ({row['label']})")
        
        # Format output by table - more concise
        for table, columns in tables.items():
            schema_description += f"{table}: {', '.join(columns)}\n"
        
        return schema_description
    except Exception as e:
        return f"Error loading schema: {str(e)}"

# System prompt for SQL query generation
SYSTEM_PROMPT = """Generate SQL queries for DuckDB. ONLY return SELECT statements - no other SQL operations allowed.

RULES:
- Return only the SQL query, no explanations
- Use proper formatting with semicolons
- Use table aliases for joins
- Add WHERE clauses to limit results

{}

{}"""

# Load database schema and examples once at startup
DATABASE_SCHEMA = load_database_schema()
EXAMPLES = load_examples()
COMPLETE_SYSTEM_PROMPT = SYSTEM_PROMPT.format(DATABASE_SCHEMA, EXAMPLES)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": COMPLETE_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        
        return jsonify({'response': ai_response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)