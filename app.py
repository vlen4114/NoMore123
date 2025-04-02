from flask import Flask, request, jsonify, render_template
from zxcvbn import zxcvbn
import hashlib
import requests
import os
import random
import string
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
app = Flask(__name__)

client = OpenAI(api_key=os.getenv('OPENAI_KEY')) if os.getenv('OPENAI_KEY') else None

# Load ML model if exists
try:
    import joblib
    model = joblib.load('models/rockyou_model.joblib')
    vectorizer = joblib.load('models/vectorizer.joblib')
except:
    model = vectorizer = None

def generate_ai_suggestions(password):
    """Get AI-powered password improvements"""
    if not client:
        return None
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""Improve this password: '{password}'. Provide:
                1. Three stronger variants 
                2. Each variant separated by "||" 
                3. No explanations
                Example: weakpass||W3akP@ss||weakPASS123"""
            }],
            temperature=0.7,
            max_tokens=100
        )
        return [s.strip() for s in response.choices[0].message.content.split('||')[:3]]
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return None

def generate_strong_variants(password):
    """Generate 3 stronger password variants locally"""
    special_chars = '!@#$%^&*'
    
    def mutate(pwd):
        # Strategy 1: Insert 2 special chars and capitalize randomly
        pwd = list(pwd)
        for _ in range(2):
            pos = random.randint(0, len(pwd))
            pwd.insert(pos, random.choice(special_chars))
        return ''.join(c.upper() if random.random() < 0.3 else c for c in pwd)
    
    def add_numbers(pwd):
        # Strategy 2: Add random numbers and a special char
        return f"{pwd}{random.randint(10,99)}{random.choice(special_chars)}"
    
    def leet_speak(pwd):
        # Strategy 3: Basic leet substitutions
        substitutions = {'a':'@','e':'3','i':'1','o':'0','s':'$'}
        return ''.join(substitutions.get(c.lower(), c) for c in pwd)
    
    return [
        mutate(password),
        add_numbers(password),
        leet_speak(password)
    ]

def analyze_password(password):
    """Core password analysis logic"""
    # Basic zxcvbn analysis
    result = zxcvbn(password)
    
    # ML prediction if model exists
    ml_weak_prob = 0
    if model:
        X = vectorizer.transform([password])
        ml_weak_prob = model.predict_proba(X)[0][0]
    
    # Breach check
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    breached = False
    try:
        response = requests.get(
            f"https://api.pwnedpasswords.com/range/{prefix}",
            timeout=3
        )
        breached = suffix in response.text
    except:
        pass
    
    # Generate suggestions for weak passwords
    suggestions = []
    if result['score'] < 3 or ml_weak_prob > 0.7:
        suggestions = generate_ai_suggestions(password) or generate_strong_variants(password)
    
    return {
        'score': result['score'],
        'feedback': result['feedback']['warning'] or "No major issues",
        'crack_time': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
        'breached': breached,
        'suggestions': suggestions,
        'used_ai': client is not None
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def api_analyze():
    password = request.json.get('password', '')
    if not password:
        return jsonify({"error": "No password provided"}), 400
    return jsonify(analyze_password(password))

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)