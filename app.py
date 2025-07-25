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

# Load industries.csv to get available industry values
def load_industries():
    try:
        industries = []
        with open('industries.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    industries.append(row[0].strip())
        
        # Remove duplicates and sort
        industries = sorted(list(set(industries)))
        return "AVAILABLE INDUSTRIES:\n" + ", ".join(industries) + "\n"
    except Exception as e:
        return f"Error loading industries: {str(e)}\n"

# Load sectors.csv to get available sector values
def load_sectors():
    try:
        sectors = []
        with open('sectors.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    sectors.append(row[0].strip())
        
        # Remove duplicates and sort
        sectors = sorted(list(set(sectors)))
        return "AVAILABLE SECTORS:\n" + ", ".join(sectors) + "\n"
    except Exception as e:
        return f"Error loading sectors: {str(e)}\n"

# Load sizes.csv to get available size values  
def load_sizes():
    try:
        sizes = []
        with open('sizes.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 0 and row[0].strip():  # Skip empty values
                    sizes.append(row[0].strip())
        
        # Remove duplicates and maintain order (Mega, Large, Mid, Small, Micro, Nano)
        size_order = ['Mega', 'Large', 'Mid', 'Small', 'Micro', 'Nano']
        sizes = [s for s in size_order if s in sizes]
        return "AVAILABLE SIZES (scalemarketcap):\n" + ", ".join(sizes) + "\n"
    except Exception as e:
        return f"Error loading sizes: {str(e)}\n"

# Load examples.csv to get example prompts and responses
def load_examples():
    try:
        examples_text = "EXAMPLES:\n"
        with open('examples.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    examples_text += f"Q: {row[0]}\nA: {row[1]}\n"
        
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

IMPORTANT FILTERING INSTRUCTIONS:
- For industry filtering, use the 'industry' column in the TICKERS table
- For sector filtering, use the 'sector' column in the TICKERS table  
- For size filtering, use the 'scalemarketcap' column in the TICKERS table

{}

{}

{}

{}

{}"""

# Load database schema, examples, industries, sectors, and sizes once at startup
DATABASE_SCHEMA = load_database_schema()
EXAMPLES = load_examples()
INDUSTRIES = load_industries()
SECTORS = load_sectors()
SIZES = load_sizes()
COMPLETE_SYSTEM_PROMPT = SYSTEM_PROMPT.format(DATABASE_SCHEMA, EXAMPLES, INDUSTRIES, SECTORS, SIZES)

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