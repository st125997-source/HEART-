from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# File paths
MODEL_PATH = 'heart_model.pkl'
ENCODERS_PATH = 'encoders.pkl'
SCALER_PATH = 'scaler.pkl'

def train_model():
    """Train and save the heart disease prediction model"""
    logger.info("Training new model...")
    
    # Sample training data (you should use the actual dataset)
    # This is a simplified version - replace with actual data loading
    data = {
        'Age': [40, 49, 37, 48, 54, 39, 45, 54, 37, 48],
        'Sex': ['M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F'],
        'ChestPainType': ['ATA', 'NAP', 'ATA', 'ASY', 'NAP', 'ATA', 'TA', 'ASY', 'NAP', 'ATA'],
        'RestingBP': [140, 160, 130, 138, 150, 120, 130, 110, 140, 120],
        'Cholesterol': [289, 180, 283, 214, 195, 339, 237, 208, 207, 229],
        'FastingBS': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'RestingECG': ['Normal', 'Normal', 'ST', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'ST', 'Normal'],
        'MaxHR': [172, 156, 98, 108, 122, 170, 170, 142, 130, 129],
        'ExerciseAngina': ['N', 'N', 'N', 'Y', 'N', 'N', 'N', 'Y', 'Y', 'Y'],
        'Oldpeak': [0, 1, 0, 1.5, 0, 0, 0, 1.5, 1.5, 2.6],
        'ST_Slope': ['Up', 'Flat', 'Up', 'Flat', 'Up', 'Up', 'Up', 'Flat', 'Flat', 'Flat'],
        'HeartDisease': [0, 1, 0, 1, 0, 0, 0, 1, 1, 1]
    }
    
    df = pd.DataFrame(data)
    
    # Prepare features
    categorical_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
    numerical_cols = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak']
    
    # Create encoders
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
    
    # Scale numerical features
    scaler = StandardScaler()
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    
    # Prepare X and y
    X = df.drop('HeartDisease', axis=1)
    y = df['HeartDisease']
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save everything
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(ENCODERS_PATH, 'wb') as f:
        pickle.dump(encoders, f)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    logger.info("Model trained and saved successfully!")
    return model, encoders, scaler

# Load or train model on startup
logger.info("Loading model...")
if os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH) and os.path.exists(SCALER_PATH):
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(ENCODERS_PATH, 'rb') as f:
            encoders = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model, encoders, scaler = train_model()
else:
    model, encoders, scaler = train_model()

@app.route('/')
def home():
    """Home page with input form"""
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for predictions"""
    logger.info("Prediction request received")
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
                          'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
                          'Oldpeak', 'ST_Slope']
        
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        # Prepare input
        input_data = {}
        
        # Encode categorical variables
        categorical_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
        for col in categorical_cols:
            try:
                input_data[col] = encoders[col].transform([data[col]])[0]
            except Exception as e:
                return jsonify({'error': f'Invalid value for {col}: {data[col]}'}), 400
        
        # Get numerical variables
        numerical_cols = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak']
        numerical_data = []
        for col in numerical_cols:
            try:
                numerical_data.append(float(data[col]))
                input_data[col] = float(data[col])
            except ValueError:
                return jsonify({'error': f'Invalid number for {col}'}), 400
        
        # Create DataFrame with correct column order
        feature_order = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
                        'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
                        'Oldpeak', 'ST_Slope']
        
        input_df = pd.DataFrame([input_data], columns=feature_order)
        
        # Scale numerical features
        input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probabilities = model.predict_proba(input_df)[0]
        
        logger.info(f"Prediction: {prediction}, Probabilities: {probabilities}")
        
        response = {
            'success': True,
            'prediction': 'Heart Disease' if prediction == 1 else 'No Heart Disease',
            'prediction_id': int(prediction),
            'probability': float(probabilities[1]),  # Probability of heart disease
            'risk_level': 'High Risk' if probabilities[1] > 0.7 else 'Moderate Risk' if probabilities[1] > 0.4 else 'Low Risk'
        }
        
        logger.info(f"Sending response: {response}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'encoders_loaded': encoders is not None,
        'scaler_loaded': scaler is not None
    })

@app.route('/options')
def options():
    """Get valid options for categorical fields"""
    return jsonify({
        'Sex': ['M', 'F'],
        'ChestPainType': ['ATA', 'NAP', 'ASY', 'TA'],
        'RestingECG': ['Normal', 'ST', 'LVH'],
        'ExerciseAngina': ['Y', 'N'],
        'ST_Slope': ['Up', 'Flat', 'Down']
    })

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
