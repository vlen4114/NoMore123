import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
import random
import string

def generate_strong_password(length=12):
    """Generate a strong password for training"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def train():
    os.makedirs('models', exist_ok=True)
    
    # Load RockYou (weak passwords)
    print("Loading weak passwords...")
    weak = pd.read_csv('data/rockyou.txt', 
                      header=None,
                      names=['password'],
                      encoding='latin-1',
                      on_bad_lines='skip').sample(10000)
    weak['label'] = 0  # 0 = weak
    
    # Generate strong passwords
    print("Generating strong passwords...")
    strong = pd.DataFrame({
        'password': [generate_strong_password() for _ in range(10000)],
        'label': 1  # 1 = strong
    })
    
    # Combine datasets
    df = pd.concat([weak, strong]).sample(frac=1)  # Shuffle
    
    # Feature engineering
    print("Extracting features...")
    vectorizer = CountVectorizer(
        analyzer='char',
        ngram_range=(1, 3),
        max_features=10000
    )
    X = vectorizer.fit_transform(df['password'])
    
    # Train model
    print("Training model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X, df['label'])
    
    # Save models
    joblib.dump(model, 'models/rockyou_model.joblib')
    joblib.dump(vectorizer, 'models/vectorizer.joblib')
    print("✅ Model trained and saved!")

if __name__ == '__main__':
    train()