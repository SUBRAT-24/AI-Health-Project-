from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('exercise', __name__, url_prefix='/api/exercise')

@bp.route('/recommendations', methods=['POST'])
@jwt_required()
def get_exercise_recommendations():
    """Get personalized exercise recommendations"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        age = data.get('age')
        fitness_level = data.get('fitness_level', 'beginner')  # beginner, intermediate, advanced
        health_condition = data.get('health_condition', 'normal')
        goals = data.get('goals', [])  # weight_loss, muscle_gain, endurance, etc.
        
        recommendations = {
            'daily_recommendation': [],
            'weekly_plan': [],
            'tips': [],
            'cautions': []
        }
        
        # Base recommendations based on fitness level
        if fitness_level == 'beginner':
            recommendations['daily_recommendation'] = [
                {
                    'exercise': 'Walking',
                    'duration': 30,
                    'intensity': 'low',
                    'calories_burned': 150,
                    'description': 'Brisk walking in fresh air'
                },
                {
                    'exercise': 'Stretching',
                    'duration': 10,
                    'intensity': 'low',
                    'calories_burned': 30,
                    'description': 'Basic flexibility exercises'
                }
            ]
            recommendations['weekly_plan'] = [
                'Monday: Walking + Stretching',
                'Tuesday: Yoga (20 mins)',
                'Wednesday: Swimming (20 mins)',
                'Thursday: Walking + Stretching',
                'Friday: Light aerobics',
                'Saturday: Outdoor activity',
                'Sunday: Rest day'
            ]
        elif fitness_level == 'intermediate':
            recommendations['daily_recommendation'] = [
                {
                    'exercise': 'Running',
                    'duration': 30,
                    'intensity': 'moderate',
                    'calories_burned': 300,
                    'description': 'Moderate paced running'
                },
                {
                    'exercise': 'Strength Training',
                    'duration': 20,
                    'intensity': 'moderate',
                    'calories_burned': 150,
                    'description': 'Bodyweight exercises'
                }
            ]
        else:  # advanced
            recommendations['daily_recommendation'] = [
                {
                    'exercise': 'High Intensity Interval Training (HIIT)',
                    'duration': 30,
                    'intensity': 'high',
                    'calories_burned': 400,
                    'description': 'Intense cardio intervals'
                },
                {
                    'exercise': 'Weight Training',
                    'duration': 45,
                    'intensity': 'high',
                    'calories_burned': 350,
                    'description': 'Progressive resistance training'
                }
            ]
        
        # Add tips
        recommendations['tips'] = [
            'Stay hydrated throughout exercise',
            'Warm up before starting',
            'Cool down after exercise',
            'Consistency is key',
            'Listen to your body',
            'Rest is essential for recovery'
        ]
        
        # Add cautions
        if health_condition == 'heart_disease':
            recommendations['cautions'].append('Consult your doctor before starting exercise')
            recommendations['cautions'].append('Avoid high intensity activities')
        if health_condition == 'arthritis':
            recommendations['cautions'].append('Focus on low impact exercises')
            recommendations['cautions'].append('Avoid jumping exercises')
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/log', methods=['POST'])
@jwt_required()
def log_exercise():
    """Log completed exercise"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Store exercise log (would go to database)
        exercise_log = {
            'user_id': user_id,
            'exercise_name': data.get('exercise_name'),
            'duration_minutes': data.get('duration_minutes'),
            'calories_burned': data.get('calories_burned'),
            'intensity': data.get('intensity'),
            'timestamp': data.get('timestamp'),
            'notes': data.get('notes')
        }
        
        return jsonify({
            'message': 'Exercise logged successfully',
            'log': exercise_log
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_exercise_history():
    """Get user's exercise history"""
    try:
        user_id = get_jwt_identity()
        
        # Get from database (placeholder)
        history = {
            'total_exercises_this_month': 15,
            'total_calories_burned': 4500,
            'weekly_average': 64.3,
            'favorite_exercise': 'Yoga',
            'recent_exercises': [
                {'date': '2026-02-12', 'exercise': 'Yoga', 'duration': 30, 'calories': 150},
                {'date': '2026-02-11', 'exercise': 'Running', 'duration': 25, 'calories': 250},
                {'date': '2026-02-10', 'exercise': 'Swimming', 'duration': 40, 'calories': 300}
            ]
        }
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
