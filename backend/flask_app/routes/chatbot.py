from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random

bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')

# Sample health-related responses
health_responses = {
    'fever': [
        'A fever is your body\'s way of fighting infection. Rest, stay hydrated, and monitor your temperature. Seek medical care if it exceeds 103°F.',
        'For fever: Stay in bed, drink plenty of water, take OTC fever reducers like acetaminophen or ibuprofen if needed.'
    ],
    'cold': [
        'For a common cold: Get plenty of rest, stay hydrated, use throat lozenges, and get vitamin C. Most colds resolve in 7-10 days.',
        'Cold symptoms can be managed with over-the-counter medications. Consult a doctor if symptoms persist.'
    ],
    'exercise': [
        'Regular exercise helps maintain health. Aim for at least 150 minutes of moderate activity weekly.',
        'Exercise benefits: improved fitness, better mental health, and disease prevention.'
    ],
    'diet': [
        'A balanced diet includes vegetables, fruits, whole grains, protein, and healthy fats.',
        'Tips: Eat colorful foods, limit processed foods, and drink plenty of water.'
    ],
    'sleep': [
        'Getting 7-9 hours of quality sleep is essential for health and recovery.',
        'Sleep tips: Maintain a consistent schedule, keep your room cool and dark, avoid screens before bed.'
    ],
    'stress': [
        'Manage stress through meditation, exercise, deep breathing, or talking to someone.',
        'Chronic stress can affect your health. Consider professional help if needed.'
    ]
}

@bp.route('/message', methods=['POST'])
@jwt_required()
def chat_message():
    """Process chatbot messages"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message', '').lower()
        
        # Simple keyword matching (can be enhanced with NLP)
        response = "I'm here to help! You can ask me about health tips, symptoms, exercise, diet, or check your health data."
        
        for keyword, responses in health_responses.items():
            if keyword in message:
                response = random.choice(responses)
                break
        
        # Add specific handling for certain queries
        if 'appointment' in message:
            response = 'To book an appointment, go to the Appointments section in your dashboard and click "Book Appointment".'
        elif 'medicine' in message:
            response = 'You can track your medications in the Dashboard. Add medicine with dosage and frequency information.'
        elif 'report' in message:
            response = 'Upload your medical reports in the Reports section. Our AI will analyze them for you.'
        elif 'recommendation' in message or 'suggest' in message:
            response = 'Based on your health profile, check the Diet and Exercise sections for personalized recommendations.'
        
        return jsonify({
            'message': message,
            'reply': response,
            'timestamp': None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/health-tips', methods=['GET'])
def get_health_tips():
    """Get daily health tips"""
    try:
        tips = [
            '💧 Drink at least 8 glasses of water daily for optimal hydration.',
            '🥗 Include leafy greens in your daily diet for essential nutrients.',
            '🚴 Exercise for 30 minutes daily to maintain cardiovascular health.',
            '😴 Maintain a consistent sleep schedule of 7-9 hours.',
            '🎯 Keep your BMI within 18.5-24.9 for optimal health.',
            '🧘 Practice meditation or deep breathing for stress relief.',
            '🎉 Stay socially connected for mental health benefits.',
            '🚭 Avoid smoking and limit alcohol consumption.',
            '🔔 Get regular health check-ups at least annually.',
            '📱 Monitor your health metrics regularly.'
        ]
        
        return jsonify({'tips': tips}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/faq', methods=['GET'])
def get_faq():
    """Get frequently asked questions"""
    try:
        faqs = [
            {
                'question': 'How do I track my health metrics?',
                'answer': 'Go to Dashboard and click "Add Health Data" to enter your current health metrics like heart rate, blood pressure, and weight.'
            },
            {
                'question': 'How can I get diet recommendations?',
                'answer': 'Visit the Diet section to get personalized dietary recommendations based on your health profile and goals.'
            },
            {
                'question': 'How do I book a doctor appointment?',
                'answer': 'Go to the Appointments section and click "Book Appointment" to schedule a consultation with a doctor.'
            },
            {
                'question': 'How can I upload medical reports?',
                'answer': 'Use the Reports section to upload your medical test results. Our AI will analyze them.'
            },
            {
                'question': 'Is my data secure?',
                'answer': 'Yes, we use encryption and follow healthcare data protection guidelines to keep your information secure.'
            }
        ]
        
        return jsonify({'faqs': faqs}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
