"""
AI Health Assistant - Chatbot Routes
Powered by Google Gemini API for intelligent health conversations.
Falls back to built-in health knowledge when API is unavailable.
Supports text, image, and file analysis.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import traceback
import re

bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')

# ─── GEMINI CONFIGURATION ────────────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv(
    'GEMINI_API_KEY',
    'AIzaSyAdgXsH9Pug7ox3TcvQ_yaC928AHcuBl_k'
)

# Initialize Gemini client (new SDK)
gemini_client = None
gemini_types = None
try:
    from google import genai
    from google.genai import types as gtypes
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    gemini_types = gtypes
    print('[CHATBOT] Gemini SDK loaded successfully')
except Exception as e:
    print(f'[CHATBOT] Gemini SDK not available, using fallback: {e}')

# System prompt that guides the AI
SYSTEM_PROMPT = """You are HealthAI, a friendly and knowledgeable AI health assistant.
Your role is to:
1. Answer health-related questions accurately and clearly
2. Provide practical wellness tips, diet advice, exercise guidance, and mental health support
3. Analyze medical reports, lab results, prescriptions, and health-related images when provided
4. Give actionable suggestions with clear formatting (use bullet points, numbered lists)
5. Always recommend consulting a qualified doctor for serious concerns
6. Be empathetic, supportive, and encouraging

Formatting rules:
- Use **bold** for important terms
- Use bullet points (•) for lists
- Keep responses concise but thorough (150-300 words ideal)
- End with a relevant health tip or suggestion when appropriate

Important disclaimers:
- You are NOT a replacement for professional medical advice
- Always suggest consulting a healthcare provider for diagnoses and treatments
"""

# Conversation history per user
user_conversations = {}

# ─── BUILT-IN HEALTH KNOWLEDGE (fallback) ────────────────────────────────────────

HEALTH_KNOWLEDGE = {
    'heart rate': '**Normal Resting Heart Rate:**\n• Adults: 60-100 beats per minute (bpm)\n• Athletes: 40-60 bpm\n• Children (6-15): 70-100 bpm\n\n**Tips to maintain healthy heart rate:**\n• Regular cardiovascular exercise (30 min/day)\n• Manage stress through meditation\n• Limit caffeine and alcohol\n• Stay hydrated\n• Get adequate sleep (7-9 hours)\n\n💡 **Tip:** If your resting heart rate is consistently above 100 bpm or below 60 bpm (without being athletic), consult a cardiologist.',

    'breakfast': '**Healthy Breakfast Ideas:**\n\n🥣 **Option 1 — Oatmeal Power Bowl**\n• Rolled oats with almond milk\n• Topped with berries, banana, chia seeds\n• Drizzle of honey\n\n🥑 **Option 2 — Avocado Toast**\n• Whole grain bread\n• Mashed avocado with lemon\n• Poached egg, cherry tomatoes\n\n🥤 **Option 3 — Green Smoothie**\n• Spinach, banana, peanut butter\n• Greek yogurt, almond milk\n\n🥚 **Option 4 — Protein Plate**\n• Scrambled eggs\n• Whole wheat toast\n• Fresh fruit salad\n\n💡 **Tip:** Eat breakfast within 1 hour of waking up to kickstart your metabolism!',

    'exercise': '**Best Exercises for Beginners:**\n\n🚶 **1. Walking** (20-30 min/day)\n• Low impact, great for cardio\n• Start with brisk walks\n\n🧘 **2. Yoga** (15-20 min)\n• Improves flexibility and balance\n• Try: Cat-Cow, Downward Dog, Warrior poses\n\n🏊 **3. Swimming**\n• Full body, joint-friendly workout\n\n💪 **4. Bodyweight Exercises**\n• Squats: 3 sets of 10\n• Push-ups: 3 sets of 5-10\n• Planks: Hold 20-30 seconds\n\n🚴 **5. Cycling** (15-20 min)\n• Great for legs and cardio\n\n**Weekly Plan:**\n• Mon/Wed/Fri: Cardio (walking/cycling)\n• Tue/Thu: Strength training\n• Sat: Yoga/stretching\n• Sun: Rest day\n\n💡 **Tip:** Start slow and increase intensity gradually. Consistency is more important than intensity!',

    'sleep': '**Tips for Better Sleep:**\n\n🌙 **Sleep Hygiene Practices:**\n• **Consistent schedule** — Sleep and wake at the same time daily\n• **Dark room** — Use blackout curtains or eye mask\n• **Cool temperature** — Keep bedroom at 65-68°F (18-20°C)\n• **No screens** — Avoid phones/laptops 1 hour before bed\n• **Limit caffeine** — No coffee after 2 PM\n\n🧘 **Relaxation Techniques:**\n• Deep breathing (4-7-8 technique)\n• Progressive muscle relaxation\n• Gentle stretching before bed\n• Warm bath or shower\n\n🍽️ **Evening Nutrition:**\n• Light dinner 3 hours before bed\n• Chamomile tea or warm milk\n• Avoid alcohol and spicy foods\n\n**Ideal Sleep Duration by Age:**\n• Adults: 7-9 hours\n• Teens: 8-10 hours\n• Children: 9-12 hours\n\n💡 **Tip:** If you can\'t fall asleep in 20 minutes, get up and do something calming, then try again.',

    'blood pressure': '**Managing Blood Pressure:**\n\n📊 **Normal Ranges:**\n• Normal: Below 120/80 mmHg\n• Elevated: 120-129 / <80\n• High (Stage 1): 130-139 / 80-89\n• High (Stage 2): 140+ / 90+\n\n🥗 **Dietary Changes (DASH Diet):**\n• Increase fruits, vegetables, whole grains\n• Reduce sodium (<2,300 mg/day)\n• Limit processed and fried foods\n• Eat potassium-rich foods (bananas, potatoes)\n\n🏃 **Lifestyle Modifications:**\n• Exercise 30 min/day, 5 days/week\n• Maintain healthy weight (BMI 18.5-24.9)\n• Limit alcohol consumption\n• Quit smoking\n• Manage stress\n\n💡 **Tip:** Monitor your blood pressure regularly at home and keep a log for your doctor.',

    'stress': '**Stress Relief Techniques:**\n\n🧘 **Immediate Relief (5-10 min):**\n• **Box breathing:** Inhale 4s → Hold 4s → Exhale 4s → Hold 4s\n• **Progressive muscle relaxation**\n• **5-4-3-2-1 grounding:** Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste\n\n📅 **Daily Practices:**\n• Meditation (10-15 min/day)\n• Journaling — write down thoughts\n• Physical exercise\n• Spending time in nature\n• Listening to calming music\n\n🤝 **Social Support:**\n• Talk to friends or family\n• Join support groups\n• Consider therapy or counseling\n\n❌ **Avoid:**\n• Excessive caffeine\n• Social media overload\n• Skipping meals\n• Isolation\n\n💡 **Tip:** Chronic stress can affect your immune system, heart, and mental health. If stress feels unmanageable, seek professional help.',

    'diabetes': '**Understanding Diabetes:**\n\n**Common Symptoms:**\n• Increased thirst and frequent urination\n• Unexplained weight loss\n• Fatigue and weakness\n• Blurred vision\n• Slow-healing wounds\n• Tingling in hands/feet\n\n📊 **Blood Sugar Levels:**\n• Normal fasting: 70-100 mg/dL\n• Pre-diabetic: 100-125 mg/dL\n• Diabetic: 126+ mg/dL\n\n🥗 **Management Tips:**\n• Monitor blood sugar regularly\n• Follow a balanced, low-glycemic diet\n• Exercise regularly (150 min/week)\n• Take medications as prescribed\n• Regular eye and foot checkups\n\n⚠️ **When to See a Doctor:**\n• Any of the above symptoms persist\n• Family history of diabetes\n• BMI over 25 with risk factors\n\n💡 **Tip:** Early detection is key. Get fasting blood sugar tested annually if you\'re over 35.',

    'headache': '**Managing Headaches:**\n\n**Common Types:**\n• **Tension headache** — Band-like pressure around head\n• **Migraine** — Throbbing, often one-sided, with nausea\n• **Cluster headache** — Severe pain around one eye\n\n🏥 **Immediate Relief:**\n• Rest in a quiet, dark room\n• Apply cold compress to forehead\n• Stay hydrated\n• Gentle neck and shoulder stretches\n• OTC pain relief (acetaminophen/ibuprofen)\n\n🛡️ **Prevention:**\n• Regular sleep schedule\n• Manage stress\n• Stay hydrated (8+ glasses/day)\n• Limit screen time\n• Regular meals (don\'t skip!)\n\n⚠️ **See a Doctor if:**\n• Sudden, severe headache ("worst ever")\n• Headache with fever, stiff neck\n• After a head injury\n• Progressive worsening over days\n\n💡 **Tip:** Keep a headache diary to identify your triggers!',

    'yoga': '**Yoga for Beginners:**\n\n🧘 **Essential Poses:**\n\n**1. Mountain Pose (Tadasana)**\n• Stand tall, feet together, arms at sides\n• Focus on alignment and breathing\n\n**2. Cat-Cow Stretch**\n• On hands and knees, alternate arching and rounding back\n• Great for spinal flexibility\n\n**3. Downward Dog**\n• Inverted V-shape, hands and feet on ground\n• Stretches hamstrings, shoulders, calves\n\n**4. Warrior I & II**\n• Builds leg strength and balance\n• Hold for 5-10 breaths each side\n\n**5. Child\'s Pose (Balasana)**\n• Resting pose, kneeling with arms extended\n• Great for relaxation\n\n**6. Tree Pose (Vrksasana)**\n• Balance on one leg, other foot on inner thigh\n• Improves balance and focus\n\n**Beginner Tips:**\n• Start with 15-20 minutes\n• Use a yoga mat for cushioning\n• Don\'t force any pose — listen to your body\n• Focus on breathing throughout\n\n💡 **Tip:** Yoga improves flexibility, reduces stress, and strengthens your core. Practice 3-4 times per week for best results!',

    'water': '**Daily Water Intake Guide:**\n\n💧 **Recommended Intake:**\n• Men: ~3.7 liters (13 cups) per day\n• Women: ~2.7 liters (9 cups) per day\n• Children: 5-8 cups depending on age\n\n**Signs of Dehydration:**\n• Dark yellow urine\n• Dry mouth and lips\n• Fatigue and dizziness\n• Headache\n• Decreased urination\n\n**Tips to Drink More Water:**\n• Carry a reusable water bottle\n• Set hourly reminders\n• Drink a glass before each meal\n• Flavor with lemon, cucumber, or berries\n• Eat water-rich foods (watermelon, cucumber)\n\n**When You Need Extra Water:**\n• During exercise\n• In hot weather\n• When sick (fever, vomiting)\n• During pregnancy/breastfeeding\n\n💡 **Tip:** Your urine should be pale yellow — that\'s the simplest hydration indicator!',

    'cold': '**Managing Common Cold:**\n\n**Symptoms:**\n• Runny/stuffy nose, sneezing\n• Sore throat, cough\n• Mild body aches, fatigue\n• Low-grade fever\n\n🏥 **Home Remedies:**\n• **Rest** — Your body needs energy to fight\n• **Hydrate** — Water, warm tea, broth\n• **Honey** — Soothes sore throat (1 tbsp in warm water)\n• **Steam inhalation** — Clears nasal congestion\n• **Salt water gargle** — Eases sore throat\n• **Vitamin C** — Oranges, kiwi, supplements\n\n💊 **OTC Medications:**\n• Decongestants for stuffy nose\n• Antihistamines for sneezing/runny nose\n• Acetaminophen for fever/aches\n\n⚠️ **See a Doctor if:**\n• Fever above 103°F (39.4°C)\n• Symptoms last more than 10 days\n• Difficulty breathing\n• Severe ear pain\n\n💡 **Tip:** Most colds resolve in 7-10 days. Wash hands frequently to prevent spreading!',

    'fever': '**Managing Fever:**\n\n**Temperature Ranges:**\n• Normal: 97-99°F (36.1-37.2°C)\n• Low-grade fever: 99-100.4°F\n• Fever: 100.4°F+ (38°C+)\n• High fever: 103°F+ (39.4°C+)\n\n🏥 **Home Care:**\n• Rest and sleep\n• Drink plenty of fluids\n• Light, breathable clothing\n• Cool compress on forehead\n• Lukewarm (not cold) bath\n• Take acetaminophen or ibuprofen\n\n⚠️ **Seek Medical Help if:**\n• Temperature above 103°F (39.4°C)\n• Fever lasting more than 3 days\n• Severe headache or stiff neck\n• Rash, confusion, or difficulty breathing\n• In infants under 3 months with any fever\n\n💡 **Tip:** Fever is your body\'s natural defense mechanism. It helps fight infection.',

    'weight': '**Healthy Weight Management:**\n\n📊 **BMI Categories:**\n• Underweight: Below 18.5\n• Normal: 18.5-24.9\n• Overweight: 25-29.9\n• Obese: 30+\n\n🥗 **Healthy Eating:**\n• Eat balanced meals with protein, fiber, and healthy fats\n• Practice portion control\n• Avoid processed and sugary foods\n• Eat slowly — it takes 20 min to feel full\n• Don\'t skip meals\n\n🏃 **Exercise Plan:**\n• 150 min moderate exercise per week\n• Combine cardio + strength training\n• Walk 10,000 steps daily\n\n**Sustainable Weight Loss:**\n• Aim for 1-2 lbs/week (0.5-1 kg)\n• Focus on habits, not quick fixes\n• Get enough sleep (7-9 hrs)\n• Manage stress\n\n💡 **Tip:** Sustainable weight management is about lifestyle changes, not crash diets!',

    'doctor': '**When Should You See a Doctor?**\n\n🚨 **Emergency — Go to ER immediately:**\n• Chest pain or pressure\n• Difficulty breathing\n• Sudden severe headache\n• Loss of consciousness\n• Uncontrolled bleeding\n• Signs of stroke (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call)\n\n⚠️ **See a Doctor Soon:**\n• Fever lasting more than 3 days\n• Unexplained weight loss/gain\n• Persistent pain anywhere\n• Changes in vision\n• Blood in urine or stool\n• Unusual lumps or growths\n• Persistent fatigue\n\n📋 **Regular Checkups:**\n• Annual physical exam\n• Blood pressure check\n• Blood sugar test (if over 35)\n• Cholesterol screening\n• Cancer screenings (age-appropriate)\n• Dental checkup (every 6 months)\n• Eye exam (every 1-2 years)\n\n💡 **Tip:** Prevention is better than cure. Regular checkups catch problems early!',

    'diet': '**Balanced Diet Guidelines:**\n\n🍽️ **Daily Plate Composition:**\n• **50% Vegetables & Fruits** — Colorful variety\n• **25% Whole Grains** — Brown rice, quinoa, oats\n• **25% Protein** — Lean meat, fish, beans, tofu\n• Plus healthy fats — Olive oil, nuts, avocado\n\n**Essential Nutrients:**\n• **Protein** — Muscle repair (0.8g per kg body weight)\n• **Fiber** — Digestion (25-30g/day)\n• **Iron** — Energy (leafy greens, red meat)\n• **Calcium** — Bones (dairy, fortified foods)\n• **Omega-3** — Brain health (fish, walnuts)\n\n**Tips:**\n• Eat 5 servings of fruits/vegetables daily\n• Choose whole grains over refined\n• Limit added sugar to <25g/day\n• Reduce sodium to <2,300mg/day\n• Cook at home more often\n\n💡 **Tip:** No single food is "bad" — it\'s about balance and moderation!',

    'medicine': '**Medication Safety Tips:**\n\n💊 **General Rules:**\n• Always take as prescribed by your doctor\n• Read labels and follow dosage instructions\n• Don\'t share medications with others\n• Store in cool, dry place away from children\n• Check expiration dates regularly\n\n⚠️ **Important Reminders:**\n• Inform your doctor about ALL medications\n• Report side effects immediately\n• Don\'t stop medications without consulting doctor\n• Use a pill organizer for multiple medications\n• Set reminders for doses\n\n💡 **Tip:** You can track your medications in our Dashboard. Add medicine name, dosage, and frequency!',

    'appointment': '**Booking a Doctor\'s Appointment:**\n\nYou can easily manage appointments through our platform!\n\n📋 **How to Book:**\n1. Go to the **Appointments** section in your dashboard\n2. Click **"Book Appointment"**\n3. Select doctor, date, and time\n4. Add notes about your concern\n5. Confirm your booking\n\n**Tips for Your Visit:**\n• Write down symptoms and questions beforehand\n• Bring a list of current medications\n• Bring previous test results if relevant\n• Arrive 10-15 minutes early\n\n💡 **Tip:** Regular checkups are essential for preventive care!',

    'report': '**Uploading Medical Reports:**\n\nYou can upload and analyze your medical reports on our platform!\n\n📄 **How to Upload:**\n1. Go to the **Reports** section\n2. Click **"Upload Report"**\n3. Select your file (PDF or image)\n4. Our AI will analyze it and provide insights\n\n**Supported Reports:**\n• Blood test results (CBC, lipid panel)\n• Urine analysis\n• X-rays and scans\n• Prescriptions\n• Discharge summaries\n\n💡 **Tip:** You can also upload images directly in this chat using the 📎 button!',
}

DEFAULT_RESPONSE = """I'm your **HealthAI Assistant** and I'm here to help! 🏥

You can ask me about:
• **Symptoms** — headaches, fever, cold, etc.
• **Diet & Nutrition** — breakfast ideas, balanced diet
• **Exercise** — workouts for beginners, yoga poses
• **Wellness** — sleep tips, stress relief, hydration
• **Health Metrics** — heart rate, blood pressure, BMI
• **Platform Help** — appointments, reports, medications

📎 **Upload an image or PDF** for medical report analysis!

💡 Try asking: "What are the symptoms of diabetes?" or "Suggest a healthy breakfast" """


def find_fallback_response(message):
    """Find best matching response from built-in knowledge"""
    msg = message.lower()
    best_match = None
    best_score = 0

    for keyword, response in HEALTH_KNOWLEDGE.items():
        # Check for keyword match
        words = keyword.split()
        score = sum(1 for w in words if w in msg)
        if score > best_score:
            best_score = score
            best_match = response

    # Also check for partial matches
    if best_score == 0:
        for keyword, response in HEALTH_KNOWLEDGE.items():
            if any(w in msg for w in keyword.split()):
                return response

    return best_match if best_match else DEFAULT_RESPONSE


def get_user_history(user_id):
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    return user_conversations[user_id]


def add_to_history(user_id, role, text):
    history = get_user_history(user_id)
    history.append({'role': role, 'text': text})
    if len(history) > 20:
        user_conversations[user_id] = history[-20:]


# ─── CHAT MESSAGE ENDPOINT ──────────────────────────────────────────────────────

@bp.route('/message', methods=['POST'])
@jwt_required()
def chat_message():
    """Process a text chat message — Gemini with fallback"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        reply = None

        # Try Gemini first
        if gemini_client and gemini_types:
            try:
                history = get_user_history(user_id)

                # Build contents
                contents = []
                for h in history:
                    contents.append(gemini_types.Content(
                        role=h['role'],
                        parts=[gemini_types.Part.from_text(text=h['text'])]
                    ))
                contents.append(gemini_types.Content(
                    role='user',
                    parts=[gemini_types.Part.from_text(text=message)]
                ))

                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=contents,
                    config=gemini_types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7,
                        max_output_tokens=1024,
                    )
                )
                reply = response.text
                print(f'[CHATBOT] Gemini response OK for user {user_id}')

            except Exception as gemini_error:
                error_str = str(gemini_error)
                print(f'[CHATBOT] Gemini failed, using fallback: {error_str[:100]}')
                reply = None  # Fall through to fallback

        # Fallback: Built-in health knowledge
        if not reply:
            reply = find_fallback_response(message)

        # Store in history
        add_to_history(user_id, 'user', message)
        add_to_history(user_id, 'model', reply)

        return jsonify({
            'response': reply,
            'reply': reply,
            'timestamp': None
        }), 200

    except Exception as e:
        print(f'[CHATBOT ERROR] {str(e)}')
        traceback.print_exc()
        return jsonify({
            'response': find_fallback_response(data.get('message', '') if 'data' in dir() else ''),
            'error': str(e)
        }), 200


# ─── IMAGE / FILE ANALYSIS ENDPOINT ─────────────────────────────────────────────

@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_file():
    """Analyze an uploaded image or file with Gemini Vision"""
    try:
        user_id = int(get_jwt_identity())

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'Empty file'}), 400

        file_data = file.read()
        mime_type = file.content_type or 'image/jpeg'
        user_message = request.form.get('message', 'Please analyze this file and provide health insights.')

        is_image = mime_type.startswith('image/')
        is_pdf = mime_type == 'application/pdf'

        if not is_image and not is_pdf:
            return jsonify({'error': 'Please upload an image (JPG, PNG) or PDF file'}), 400

        reply = None

        # Try Gemini Vision
        if gemini_client and gemini_types:
            try:
                parts = [
                    gemini_types.Part.from_text(text=user_message),
                    gemini_types.Part.from_bytes(data=file_data, mime_type=mime_type)
                ]

                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[gemini_types.Content(role='user', parts=parts)],
                    config=gemini_types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7,
                        max_output_tokens=2048,
                    )
                )
                reply = response.text
            except Exception as e:
                print(f'[ANALYZE] Gemini vision failed: {str(e)[:100]}')

        if not reply:
            reply = f"📄 I received your file **{file.filename}** but the AI analysis service is temporarily unavailable.\n\n**What you can do:**\n• Try uploading again in a few minutes\n• Make sure the image is clear and well-lit\n• For medical reports, ensure text is readable\n\n💡 **Tip:** In the meantime, you can ask me health questions in text and I'll help!"

        add_to_history(user_id, 'user', f'[Uploaded {file.filename}] {user_message}')
        add_to_history(user_id, 'model', reply)

        return jsonify({
            'response': reply,
            'reply': reply,
            'filename': file.filename,
            'file_type': 'image' if is_image else 'pdf',
        }), 200

    except Exception as e:
        print(f'[ANALYZE ERROR] {str(e)}')
        return jsonify({
            'response': 'Sorry, I could not analyze the file. Please try again.',
            'error': str(e)
        }), 200


# ─── SUGGESTIONS ─────────────────────────────────────────────────────────────────

@bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    suggestions = [
        {'icon': '💓', 'text': 'What is a healthy heart rate?'},
        {'icon': '🥗', 'text': 'Suggest a healthy breakfast'},
        {'icon': '🏃', 'text': 'Best exercises for beginners'},
        {'icon': '😴', 'text': 'Tips for better sleep'},
        {'icon': '💊', 'text': 'How to manage blood pressure'},
        {'icon': '🧘', 'text': 'Stress relief techniques'},
    ]
    return jsonify({'suggestions': suggestions}), 200


# ─── CLEAR HISTORY ───────────────────────────────────────────────────────────────

@bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_history():
    try:
        user_id = int(get_jwt_identity())
        if user_id in user_conversations:
            del user_conversations[user_id]
        return jsonify({'message': 'Chat history cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── HEALTH TIPS ─────────────────────────────────────────────────────────────────

@bp.route('/health-tips', methods=['GET'])
def get_health_tips():
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
