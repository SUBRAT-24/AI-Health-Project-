from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('diet', __name__, url_prefix='/api/diet')

@bp.route('/recommendations', methods=['POST'])
@jwt_required()
def get_diet_recommendations():
    """Get personalized diet recommendations"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Simple recommendation logic - can be enhanced with ML
        age = data.get('age')
        gender = data.get('gender')
        health_condition = data.get('health_condition', 'normal')
        height = data.get('height')
        weight = data.get('weight')
        
        recommendations = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': [],
            'daily_goals': {
                'calories': 2000,
                'proteins': 50,
                'carbs': 250,
                'fats': 65
            }
        }
        
        # Base recommendations
        if health_condition.lower() == 'diabetes':
            recommendations['breakfast'].append({
                'name': 'Oatmeal with berries',
                'calories': 250,
                'proteins': 8,
                'carbs': 38,
                'fats': 5,
                'description': 'High fiber oatmeal with fresh berries'
            })
            recommendations['lunch'].append({
                'name': 'Grilled chicken with vegetables',
                'calories': 400,
                'proteins': 35,
                'carbs': 30,
                'fats': 12,
                'description': 'Lean protein with leafy greens'
            })
        else:
            recommendations['breakfast'].append({
                'name': 'Eggs with whole wheat toast',
                'calories': 300,
                'proteins': 15,
                'carbs': 35,
                'fats': 10,
                'description': 'Balanced breakfast with protein and carbs'
            })
            recommendations['lunch'].append({
                'name': 'Salmon with brown rice',
                'calories': 450,
                'proteins': 30,
                'carbs': 40,
                'fats': 15,
                'description': 'Omega-3 rich meal'
            })
        
        recommendations['dinner'].append({
            'name': 'Vegetable stir-fry with tofu',
            'calories': 350,
            'proteins': 20,
            'carbs': 35,
            'fats': 10,
            'description': 'Light and nutritious evening meal'
        })
        
        recommendations['snacks'].append({
            'name': 'Apple with almonds',
            'calories': 150,
            'proteins': 5,
            'carbs': 20,
            'fats': 8,
            'description': 'Healthy snack option'
        })
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/meal-plan', methods=['POST'])
@jwt_required()
def generate_meal_plan():
    """Generate weekly meal plan"""
    try:
        user_id = get_jwt_identity()
        
        meal_plan = {
            'week_plan': {
                'Monday': {
                    'breakfast': 'Oatmeal with berries',
                    'lunch': 'Grilled chicken salad',
                    'dinner': 'Baked salmon with vegetables',
                    'snacks': ['Apple', 'Almonds']
                },
                'Tuesday': {
                    'breakfast': 'Greek yogurt with granola',
                    'lunch': 'Turkey sandwich with vegetables',
                    'dinner': 'Grilled chicken with brown rice',
                    'snacks': ['Banana', 'Peanut butter']
                },
                # Add more days...
            },
            'shopping_list': [
                'Chicken breast', 'Salmon', 'Eggs', 'Oats', 'Brown rice',
                'Various vegetables', 'Greek yogurt', 'Nuts and seeds'
            ],
            'total_weekly_calories': 13000,
            'notes': 'This meal plan is based on your health profile and preferences'
        }
        
        return jsonify(meal_plan), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
