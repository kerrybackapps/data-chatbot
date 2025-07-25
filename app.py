from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load indicators.csv to get database schema
def load_database_schema():
    try:
        df = pd.read_csv('indicators.csv')
        # Convert the CSV to a description of tables and columns
        schema_description = "The database contains the following tables and columns:\n\n"
        
        # Group by table
        for table in df['table'].unique():
            table_df = df[df['table'] == table]
            schema_description += f"Table: {table}\n"
            schema_description += "Columns:\n"
            for _, row in table_df.iterrows():
                schema_description += f"  - {row['column']} ({row['label']}): {row['description']}\n"
            schema_description += "\n"
        
        return schema_description
    except Exception as e:
        return f"Error loading database schema: {str(e)}"

# System prompt for SQL query generation
SYSTEM_PROMPT = """Your only task is to provide a SQL query based on the prompt to execute at the database with tables and columns described below. You may ask the user if you do not understand something but your only objective is to provide a SQL query. You do not provide data or links or other advice. The database description is as follows:

{}"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Load the database schema
        schema = load_database_schema()
        
        # Create the complete system prompt
        complete_system_prompt = SYSTEM_PROMPT.format(schema)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": complete_system_prompt},
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