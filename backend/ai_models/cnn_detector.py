import cv2
import numpy as np
from tensorflow import keras
import os

class CNNDiseaseDetector:
    """CNN-based disease detection from medical images"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None
        self.classes = ['normal', 'abnormal', 'uncertain']
    
    def load_model(self):
        """Load pre-trained CNN model"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
            else:
                self.model = self._build_default_model()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def _build_default_model(self):
        """Build a simple CNN model for image classification"""
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(3, activation='softmax')  # 3 classes
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            if img is None:
                return None
            
            # Resize to 224x224
            img = cv2.resize(img, (224, 224))
            
            # Normalize pixel values
            img = img.astype('float32') / 255.0
            
            return np.expand_dims(img, axis=0)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def detect_disease(self, image_path):
        """Detect disease from medical image"""
        if self.model is None:
            self.load_model()
        
        preprocessed_img = self.preprocess_image(image_path)
        
        if preprocessed_img is None:
            return {'error': 'Could not process image'}
        
        try:
            # Make prediction
            predictions = self.model.predict(preprocessed_img, verbose=0)
            
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            
            return {
                'classification': self.classes[class_idx],
                'confidence': confidence,
                'probabilities': {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.classes, predictions[0])
                },
                'recommendation': self._get_recommendation(self.classes[class_idx], confidence)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_recommendation(self, classification, confidence):
        """Get recommendation based on classification"""
        if classification == 'abnormal':
            if confidence > 0.8:
                return 'Please consult with a radiologist or doctor immediately.'
            else:
                return 'Please consult with a doctor for further evaluation.'
        elif classification == 'uncertain':
            return 'The results are uncertain. Please arrange a follow-up examination.'
        else:
            return 'Results appear normal. Continue regular health check-ups.'
    
    def batch_analyze(self, image_paths):
        """Analyze multiple images"""
        results = []
        for image_path in image_paths:
            result = self.detect_disease(image_path)
            results.append({
                'image': image_path,
                'result': result
            })
        return results
