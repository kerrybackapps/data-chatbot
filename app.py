from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
from system_prompt import get_system_prompt

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load complete system prompt once at startup
COMPLETE_SYSTEM_PROMPT = get_system_prompt()

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
        
        # Parse the JSON response
        try:
            import json
            parsed_response = json.loads(ai_response)
            communication = parsed_response.get('communication', '')
            sql_query = parsed_response.get('sql_query', '')
        except:
            # Fallback if response is not in expected JSON format
            communication = ai_response
            sql_query = ''
        
        return jsonify({
            'communication': communication,
            'sql_query': sql_query
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)