import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pickle
import os

class HealthAnalyzer:
    """AI-based health analyzer using machine learning"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None
        self.scaler = None
    
    def analyze_vital_signs(self, heart_rate, systolic, diastolic, temperature):
        """Analyze vital signs and return health status"""
        vitals = {
            'heart_rate': heart_rate,
            'systolic': systolic,
            'diastolic': diastolic,
            'temperature': temperature
        }
        
        risk_level = 'low'
        recommendations = []
        alerts = []
        
        # Heart rate analysis
        if heart_rate < 60:
            alerts.append('Low heart rate - Bradycardia')
            risk_level = 'high'
        elif heart_rate > 100:
            alerts.append('High heart rate - Tachycardia')
            risk_level = 'medium'
        
        # Blood pressure analysis
        if systolic >= 140 or diastolic >= 90:
            alerts.append('Hypertension - High blood pressure')
            risk_level = 'high'
        elif systolic >= 130 and systolic < 140 or diastolic >= 80 and diastolic < 90:
            alerts.append('Prehypertension')
            risk_level = 'medium'
        
        # Temperature analysis
        if temperature > 37.5:
            alerts.append('Fever detected')
            risk_level = 'high' if temperature > 39 else 'medium'
        elif temperature < 35:
            alerts.append('Hypothermia - Low temperature')
            risk_level = 'high'
        
        return {
            'vitals': vitals,
            'risk_level': risk_level,
            'alerts': alerts,
            'recommendations': recommendations
        }
    
    def predict_health_condition(self, features):
        """Predict potential health conditions using ML model"""
        try:
            if self.model is None:
                self.model = self._build_model()
            
            # Normalize features
            features_array = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(features_array, verbose=0)
            
            return {
                'prediction': float(prediction[0][0]),
                'confidence': float(prediction[0][0]) if prediction[0][0] > 0.5 else 1 - float(prediction[0][0])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _build_model(self):
        """Build a simple neural network model"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(10,)),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def generate_health_report(self, user_data):
        """Generate comprehensive health report"""
        report = {
            'overall_health_score': 0,
            'health_metrics': {},
            'risk_factors': [],
            'recommendations': [],
            'lifestyle_suggestions': []
        }
        
        # Calculate health score
        score = 100
        
        # Check metrics
        if user_data.get('heart_rate'):
            if 60 <= user_data['heart_rate'] <= 100:
                score -= 0
            else:
                score -= 15
        
        if user_data.get('bmi'):
            if 18.5 <= user_data['bmi'] <= 24.9:
                score -= 0
            else:
                score -= 20
        
        report['overall_health_score'] = max(0, score)
        
        # Add recommendations based on score
        if report['overall_health_score'] < 50:
            report['recommendations'].append('Consult with a healthcare professional')
        elif report['overall_health_score'] < 75:
            report['recommendations'].append('Work on lifestyle improvements')
        
        return report
