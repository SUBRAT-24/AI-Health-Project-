import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from transformers import pipeline

class NLPHealthProcessor:
    """NLP-based health data processor"""
    
    def __init__(self):
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
        except Exception as e:
            print(f"Warning: {e}")
    
    def analyze_symptoms(self, symptom_text):
        """Analyze symptom description using NLP"""
        tokens = word_tokenize(symptom_text.lower())
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        
        # Symptom keywords mapping
        symptom_keywords = {
            'fever': ['fever', 'high temp', 'temperature', 'hot'],
            'cough': ['cough', 'coughing', 'throat'],
            'cold': ['cold', 'runny nose', 'congestion'],
            'headache': ['headache', 'head pain', 'migraine'],
            'fatigue': ['tired', 'exhausted', 'fatigue', 'weak'],
            'nausea': ['nausea', 'sick', 'queasy'],
            'pain': ['pain', 'ache', 'hurt', 'sore']
        }
        
        detected_symptoms = []
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in filtered_tokens for keyword in keywords):
                detected_symptoms.append(symptom)
        
        return {
            'symptoms': detected_symptoms,
            'confidence': len(detected_symptoms) / len(symptom_keywords),
            'tokens': filtered_tokens
        }
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of health-related text"""
        try:
            result = self.sentiment_pipeline(text[:512])  # Limit to 512 tokens
            return {
                'sentiment': result[0]['label'],
                'score': result[0]['score']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def extract_health_entities(self, text):
        """Extract health-related entities from text"""
        entities = {
            'medications': [],
            'diseases': [],
            'procedures': [],
            'body_parts': []
        }
        
        # Simple pattern matching (can be enhanced with named entity recognition)
        medication_keywords = ['aspirin', 'ibuprofen', 'acetaminophen', 'metformin', 'lisinopril']
        disease_keywords = ['diabetes', 'hypertension', 'arthritis', 'asthma', 'copd']
        body_part_keywords = ['head', 'chest', 'stomach', 'arm', 'leg', 'heart', 'lung']
        
        text_lower = text.lower()
        
        for med in medication_keywords:
            if med in text_lower:
                entities['medications'].append(med)
        
        for disease in disease_keywords:
            if disease in text_lower:
                entities['diseases'].append(disease)
        
        for body_part in body_part_keywords:
            if body_part in text_lower:
                entities['body_parts'].append(body_part)
        
        return entities
    
    def generate_health_advice(self, condition):
        """Generate health advice for a condition"""
        advice_database = {
            'fever': 'Stay hydrated, rest, and monitor your temperature. Seek medical care if it exceeds 103°F.',
            'cold': 'Get plenty of rest, take vitamin C, and use saline nasal drops. Most colds resolve in 7-10 days.',
            'headache': 'Try relaxation techniques, ensure proper hydration, and rest in a quiet environment.',
            'fatigue': 'Ensure adequate sleep (7-9 hours), exercise, and eat nutritious food.',
            'hypertension': 'Reduce salt intake, exercise regularly, manage stress, and take prescribed medications.',
            'diabetes': 'Monitor blood sugar, maintain healthy diet, exercise, and take medications as prescribed.'
        }
        
        return advice_database.get(condition.lower(), 'Consult with a healthcare professional for personalized advice.')
