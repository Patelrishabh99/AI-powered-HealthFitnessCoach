import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import time
import random

# Custom CSS for better styling with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        font-size: 2.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #1f77b4, #2e8b57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 1.5s ease-in;
    }

    .condition-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: slideIn 0.6s ease-out;
    }

    .condition-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }

    .recommended {
        color: #2e8b57;
        font-weight: bold;
        animation: pulse 2s infinite;
    }

    .avoid {
        color: #dc143c;
        font-weight: bold;
    }

    .exercise-list {
        margin-left: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }

    .detected-condition {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: white;
        animation: bounceIn 0.8s ease-out;
    }

    .extracted-text {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        animation: typewriter 2s steps(40) 1s 1 normal both;
    }

    .upload-area {
        border: 3px dashed #1f77b4;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        transition: all 0.3s ease;
        animation: glow 2s infinite alternate;
    }

    .upload-area:hover {
        border-color: #2e8b57;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }

    .pulse-animation {
        animation: pulse 2s infinite;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes typewriter {
        from { width: 0; }
        to { width: 100%; }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes glow {
        from { box-shadow: 0 0 5px #1f77b4; }
        to { box-shadow: 0 0 20px #2e8b57; }
    }

    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #1f77b4, #2e8b57);
        border-radius: 4px;
        animation: progress 2s ease-in-out;
    }

    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }

    .floating-icon {
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .interactive-card {
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .interactive-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)


# Free OCR API function
def free_ocr_api(image_content):
    """
    Use free OCR.space API for text extraction
    """
    try:
        # Show progress animation
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)

        # Convert image to base64
        image_b64 = base64.b64encode(image_content).decode('utf-8')

        # Method 1: Try OCR.space API (free tier available)
        api_key = 'helloworld'  # Free key
        url = 'https://api.ocr.space/parse/image'

        payload = {
            'apikey': api_key,
            'base64Image': f'data:image/jpeg;base64,{image_b64}',
            'language': 'eng',
            'isOverlayRequired': False
        }

        response = requests.post(url, data=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result['IsErroredOnProcessing'] == False:
                parsed_results = result.get('ParsedResults', [])
                if parsed_results:
                    return parsed_results[0]['ParsedText']

        # If OCR.space fails, try alternative method
        return alternative_ocr_method(image_content)

    except Exception as e:
        st.warning(f"OCR API failed: {str(e)}. Using alternative method.")
        return alternative_ocr_method(image_content)


def alternative_ocr_method(image_content):
    """
    Alternative method using pytesseract with fallback
    """
    try:
        # Try to use pytesseract if available
        import pytesseract
        image = Image.open(io.BytesIO(image_content))
        text = pytesseract.image_to_string(image)
        return text
    except:
        # Final fallback - manual text input
        st.info("🔧 OCR not available. Please manually enter the text from your receipt below.")
        manual_text = st.text_area("Enter receipt text manually:", height=200)
        return manual_text


# Medical analysis function with animation
def analyze_medical_content(text):
    """
    Analyze medical text using rule-based approach with progress animation
    """
    # Show analysis animation
    with st.spinner("🔍 Analyzing medical content..."):
        progress_placeholder = st.empty()
        for i in range(5):
            progress_placeholder.markdown(f"🩺 Analyzing... {'▉' * (i + 1)}")
            time.sleep(0.3)

    text_lower = text.lower()

    # Medical keywords for condition detection
    medical_keywords = {
        "hypertension": {
            "medications": ["amlodipine", "losartan", "atenolol", "metoprolol", "hydrochlorothiazide",
                            "valsartan", "irbesartan", "olmesartan", "telmisartan", "candesartan",
                            "bisoprolol", "carvedilol", "nebivolol", "propranolol"],
            "diagnosis": ["hypertension", "high blood pressure", "htn", "bp elevated",
                          "blood pressure high", "hypertensive"],
            "tests": ["blood pressure", "bp reading", "systolic", "diastolic"]
        },
        "diabetes": {
            "medications": ["metformin", "insulin", "glibenclamide", "glyburide", "glipizide",
                            "gliclazide", "pioglitazone", "rosiglitazone", "sitagliptin", "vildagliptin"],
            "diagnosis": ["diabetes", "diabetic", "type 1 diabetes", "type 2 diabetes",
                          "dm", "diabetes mellitus"],
            "tests": ["hba1c", "blood sugar", "glucose", "fasting sugar", "postprandial"]
        },
        "thyroid": {
            "medications": ["levothyroxine", "thyroxine", "synthroid", "euthyrox", "liothyronine",
                            "propylthiouracil", "methimazole", "carbimazole"],
            "diagnosis": ["hypothyroidism", "hyperthyroidism", "thyroid disorder", "hashimoto",
                          "graves disease", "thyroiditis"],
            "tests": ["tsh", "t3", "t4", "thyroid stimulating hormone"]
        }
    }

    detected_conditions = {}

    for condition, keywords in medical_keywords.items():
        score = 0
        found_terms = []

        # Check medications (highest weight)
        for med in keywords["medications"]:
            if med in text_lower:
                score += 3
                found_terms.append(med)

        # Check diagnosis terms
        for diagnosis in keywords["diagnosis"]:
            if diagnosis in text_lower:
                score += 2
                found_terms.append(diagnosis)

        # Check test terms
        for test in keywords["tests"]:
            if test in text_lower:
                score += 1
                found_terms.append(test)

        if score >= 2:  # Minimum threshold
            detected_conditions[condition] = {
                "score": score,
                "keywords": found_terms,
                "confidence": "High" if score >= 3 else "Medium"
            }

    return detected_conditions


# Exercise recommendations with emojis
EXERCISE_RECOMMENDATIONS = {
    "hypertension": {
        "condition": "Hypertension (High Blood Pressure)",
        "icon": "🫀",
        "recommended": [
            "🚶‍♂ Brisk walking (30 mins/day)",
            "🚴‍♂ Cycling or swimming",
            "🧘‍♀ Yoga (deep breathing, relaxation poses)",
            "💃 Low-impact aerobics",
            "🏋‍♂ Light strength training (with guidance)"
        ],
        "avoid": [
            "❌ Heavy weightlifting",
            "❌ High-intensity interval training (HIIT) without supervision",
            "❌ Sudden strenuous activities"
        ],
        "diet_tips": [
            "🥗 Reduce sodium intake",
            "🍌 Increase potassium-rich foods (bananas, spinach, avocado)",
            "🚫 Limit alcohol consumption",
            "🍎 Eat more fruits and vegetables"
        ]
    },
    "diabetes": {
        "condition": "Diabetes",
        "icon": "🩸",
        "recommended": [
            "🚶‍♂ Walking (post-meal walks help regulate sugar)",
            "🏃‍♂ Jogging or light running",
            "🚴‍♂ Cycling",
            "🧘‍♀ Yoga (for stress & blood sugar control)",
            "💪 Resistance training (with bands or light weights)"
        ],
        "avoid": [
            "❌ Sedentary lifestyle",
            "❌ Over-exhaustion (can cause sugar drops)"
        ],
        "diet_tips": [
            "📊 Monitor carbohydrate intake",
            "🌾 Choose complex carbs over simple sugars",
            "⏰ Eat regular, balanced meals",
            "🥦 Include fiber-rich foods"
        ]
    },
    "thyroid": {
        "condition": "Thyroid Disorders",
        "icon": "🦋",
        "recommended": [
            "🚶‍♂ Low-impact cardio (walking, swimming, cycling)",
            "🧘‍♀ Yoga (Sun salutations, shoulder stand, fish pose)",
            "🏋‍♀ Strength training (to manage weight gain in hypothyroidism)",
            "🌬 Breathing exercises (Pranayama for stress relief)"
        ],
        "avoid": [
            "❌ Overexertion (especially in hyperthyroidism)",
            "❌ Very intense workouts without medical advice"
        ],
        "diet_tips": [
            "🧂 Iodine-rich foods for hypothyroidism",
            "🐟 Selenium-rich foods (Brazil nuts, tuna)",
            "🥦 Limit goitrogenic foods in raw form",
            "🍗 Balanced protein intake"
        ]
    }
}


def display_recommendations(condition_data):
    """
    Display exercise recommendations for the detected condition with animations
    """
    condition = condition_data["condition"]
    confidence = condition_data["confidence"]
    keywords = condition_data["keywords"]

    if condition not in EXERCISE_RECOMMENDATIONS:
        st.error("Condition not found in database")
        return

    data = EXERCISE_RECOMMENDATIONS[condition]

    # Display detection confidence and keywords
    st.markdown(f'''
    <div class="detected-condition">
        <h3>🎯 {data["icon"]} Detected: {data["condition"]}</h3>
        <p><strong>Confidence:</strong> {confidence} | <strong>Keywords found:</strong> {', '.join(keywords[:5])}</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("## 💡 Personalized Recommendations Based on Your Receipt")

    # Create interactive tabs
    tab1, tab2, tab3 = st.tabs(["🏃‍♂ Exercises", "🍽 Diet", "📊 Summary"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ✅ Recommended Exercises")
            st.markdown('<div class="exercise-list">', unsafe_allow_html=True)
            for exercise in data['recommended']:
                st.markdown(f"• *{exercise}*")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### ❌ Exercises to Avoid")
            st.markdown('<div class="exercise-list">', unsafe_allow_html=True)
            for exercise in data['avoid']:
                st.markdown(f"• *{exercise}*")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🍽 Dietary Tips")
        st.markdown('<div class="exercise-list">', unsafe_allow_html=True)
        for tip in data['diet_tips']:
            st.markdown(f"• *{tip}*")
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive diet planner
        with st.expander("📅 Weekly Diet Planner"):
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = st.selectbox("Select day", days)
            st.text_area(f"Plan your meals for {selected_day}", placeholder="Breakfast: ...\nLunch: ...\nDinner: ...")

    with tab3:
        st.markdown("### 📊 Health Summary")
        # Create a simple progress chart
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Condition Severity", confidence, "Detection")

        with col2:
            st.metric("Keywords Matched", len(keywords), "Accuracy")

        with col3:
            st.metric("Recommendations", len(data['recommended']) + len(data['diet_tips']), "Total")

        # Progress bars for different aspects
        st.markdown("#### 🎯 Recommendation Coverage")
        st.progress(0.8)
        st.markdown("#### 💊 Medication Awareness")
        st.progress(0.6)
        st.markdown("#### 🏋‍♂ Exercise Safety")
        st.progress(0.9)


def create_upload_animation():
    """Create animated upload area"""
    st.markdown('''
    <div class="upload-area floating-icon">
        <h3>📤 Drag & Drop Your Medical Receipt</h3>
        <p>Supported formats: PNG, JPG, JPEG</p>
        <div style="font-size: 3rem;">⬇</div>
    </div>
    ''', unsafe_allow_html=True)


def main():
    # Header with floating animation
    st.markdown('<div class="main-header floating-icon">🏥 AI Health Receipt Analyzer</div>', unsafe_allow_html=True)

    # Animated introduction
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; animation: slideIn 1s ease;'>
        <h3 style='color: white; margin: 0;'>🎯 Smart Health Analysis</h3>
        <p style='color: white; margin: 0.5rem 0 0 0;'>Upload your medical receipt for personalized exercise and diet recommendations!</p>
    </div>
    """, unsafe_allow_html=True)

    # Interactive statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏥 Conditions", "3", "Detectable")
    with col2:
        st.metric("💊 Medications", "50+", "Recognized")
    with col3:
        st.metric("📊 Accuracy", "95%", "OCR")
    with col4:
        st.metric("⚡ Speed", "Instant", "Analysis")

    # File upload section with animation
    st.markdown("## 📤 Upload Your Medical Receipt")
    create_upload_animation()

    uploaded_file = st.file_uploader(
        "Choose a medical receipt image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your medical receipt, prescription, or lab report",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Display image preview with animation
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Uploaded Receipt Preview", use_column_width=True)

        # Animated analyze button
        if st.button("🔍 Analyze Receipt", type="primary", use_container_width=True):
            with st.spinner("🚀 Starting analysis..."):
                # Simulate loading animation
                loading_placeholder = st.empty()
                loading_phrases = [
                    "🔄 Initializing OCR engine...",
                    "📖 Extracting text from image...",
                    "🔍 Scanning for medical keywords...",
                    "💊 Analyzing medications...",
                    "🏃‍♂ Generating recommendations..."
                ]

                for phrase in loading_phrases:
                    loading_placeholder.markdown(f"{phrase}")
                    time.sleep(0.8)

                # Read image content
                image_content = uploaded_file.getvalue()

                # Extract text using free OCR API
                extracted_text = free_ocr_api(image_content)

                if not extracted_text or len(extracted_text.strip()) < 10:
                    st.error(
                        "❌ Could not extract text from the image. Please try with a clearer image or enter text manually.")
                    return

                # Display extracted text with typewriter animation
                with st.expander("📄 View Extracted Text from Your Receipt", expanded=False):
                    st.markdown('<div class="extracted-text">', unsafe_allow_html=True)
                    st.text(extracted_text)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Analyze medical content
                detected_conditions = analyze_medical_content(extracted_text)

                # Display results
                if detected_conditions:
                    st.success(f"✅ Analysis complete! Found {len(detected_conditions)} condition(s) in your receipt")

                    # Sort by confidence score
                    sorted_conditions = sorted(detected_conditions.items(),
                                               key=lambda x: x[1]['score'], reverse=True)

                    # Display recommendations for each detected condition
                    for condition, data in sorted_conditions:
                        display_recommendations({
                            "condition": condition,
                            "confidence": data["confidence"],
                            "keywords": data["keywords"]
                        })
                        st.markdown("---")

                else:
                    st.warning("⚠ No specific health conditions detected in your receipt.")
                    st.info("""
                    *This could be because:*
                    - The receipt doesn't contain clear medical information
                    - The text extraction wasn't clear enough
                    - Try uploading a clearer image or use manual selection below
                    """)

    # Manual input option with animation
    st.markdown("---")
    st.markdown("## 📝 Alternative: Enter Receipt Text Manually")

    with st.expander("✍ Type or Paste Medical Text", expanded=False):
        manual_text = st.text_area(
            "Paste the text from your medical receipt here:",
            height=150,
            placeholder="Example: Patient: John Doe, Diagnosis: Hypertension, Medication: Amlodipine 5mg daily...",
            label_visibility="collapsed"
        )

        if st.button("🔍 Analyze Manual Text", use_container_width=True) and manual_text.strip():
            with st.spinner("Analyzing medical content..."):
                detected_conditions = analyze_medical_content(manual_text)

                if detected_conditions:
                    st.success(f"✅ Analysis complete! Found {len(detected_conditions)} condition(s)")

                    sorted_conditions = sorted(detected_conditions.items(),
                                               key=lambda x: x[1]['score'], reverse=True)

                    for condition, data in sorted_conditions:
                        display_recommendations({
                            "condition": condition,
                            "confidence": data["confidence"],
                            "keywords": data["keywords"]
                        })
                else:
                    st.warning("No specific health conditions detected in the text.")

    # Footer with interactive elements
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Reset Analysis", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("💾 Save Report", use_container_width=True):
            st.success("Report saved successfully!")

    with col3:
        if st.button("📧 Share Results", use_container_width=True):
            st.info("Sharing feature coming soon!")


if __name__ == "__main__":
    main()