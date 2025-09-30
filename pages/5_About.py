import streamlit as st
import base64


# Function to convert image to base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Set background image
def set_background(image_path):
    base64_img = get_base64_of_image(image_path)
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Roboto:wght@300;400;700&family=Poppins:wght@600;800&family=Oswald:wght@600;700&display=swap');

        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.9)), 
                       url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        .hero-section {{
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 3rem;
            margin: 2rem 0;
            border: 2px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }}

        .main-title {{
            font-family: 'Oswald', sans-serif;
            font-weight: 900;
            font-size: 4rem !important;
            color: #ffffff;
            text-align: center;
            text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #FF6B35, #FF8E53, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .mission-statement {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.4rem;
            color: #ffffff;
            text-align: center;
            line-height: 1.6;
            margin-bottom: 2rem;
            font-weight: 300;
        }}

        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
        }}

        .feature-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            border-left: 5px solid #FF6B35;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }}

        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}

        .feature-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}

        .feature-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #2D3748;
            margin-bottom: 0.5rem;
        }}

        .feature-desc {{
            color: #4A5568;
            line-height: 1.5;
            font-size: 0.95rem;
        }}

        .healthcare-section {{
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.9), rgba(78, 205, 196, 0.9));
            padding: 2.5rem;
            border-radius: 20px;
            margin: 2rem 0;
            color: white;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }}

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}

        .stat-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .stat-number {{
            font-size: 2.5rem;
            font-weight: 900;
            font-family: 'Oswald', sans-serif;
            color: #FF6B35;
            margin: 0;
        }}

        .stat-label {{
            color: white;
            font-family: 'Roboto', sans-serif;
            margin: 0;
        }}

        .tech-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #FF6B35, #4ECDC4);
            color: white;
            padding: 0.5rem 1.2rem;
            border-radius: 25px;
            margin: 0.3rem;
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Set page configuration
st.set_page_config(page_title="About - AI Fitness Coach", layout="wide")

# Set background image
try:
    set_background(r"C:\Users\patel\PycharmProjects\Fitness\animations\img.png")
except:
    # Fallback gradient background
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Hero Section
#st.markdown('<div class="hero-section">', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🏥 AI HEALTH & FITNESS COACH</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="mission-statement">
    <strong>Bridging the gap between fitness and healthcare</strong> through AI-powered technology that makes exercise 
    <span style="color: #FF6B35;">safe, accessible, and medically intelligent</span> for everyone.
</div>
""", unsafe_allow_html=True)

# Mission & Vision
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: rgba(255, 107, 53, 0.5); padding: 2rem; border-radius: 15px; border-left: 4px solid #FF6B35;">
        <h3 style="font-family: 'Montserrat', sans-serif; color: #FF6B35; margin-bottom: 1rem;">🎯 OUR MISSION</h3>
        <p style="font-family: 'Roboto', sans-serif; color: #E2E8F0; line-height: 1.6;">
            To prevent exercise-related injuries through real-time AI monitoring while connecting fitness 
            directly to healthcare services. We're making fitness inclusive for <strong>all abilities</strong> 
            and <strong>all needs</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(78, 205, 196, 0.1); padding: 2rem; border-radius: 15px; border-left: 4px solid #4ECDC4;">
        <h3 style="font-family: 'Montserrat', sans-serif; color: #4ECDC4; margin-bottom: 1rem;">👁️ OUR VISION</h3>
        <p style="font-family: 'Roboto', sans-serif; color: #E2E8F0; line-height: 1.6;">
            A world where everyone has access to personalized, safe fitness guidance with 
            <strong>instant medical support</strong> when needed. Where technology serves health, 
            and no one gets left behind.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close hero-section

# Features Section
st.markdown("""
<div style="text-align: center; margin: 3rem 0;">
    <h2 style="font-family: 'Oswald', sans-serif; color: white; font-size: 2.5rem; margin-bottom: 1rem;">
        🚀 CORE FEATURES
    </h2>
    <p style="font-family: 'Roboto', sans-serif; color: #CBD5E0; font-size: 1.2rem;">
        Advanced technology working together for your safety and progress
    </p>
</div>
""", unsafe_allow_html=True)

# Features Grid
st.markdown('<div class="features-grid">', unsafe_allow_html=True)

features = [
    {
        "icon": "🤖",
        "title": "AI Pose Detection & Form Correction",
        "desc": "Real-time body tracking with instant feedback on exercise form to prevent injuries"
    },
    {
        "icon": "🎯",
        "title": "Voice-Guided Workouts",
        "desc": "Hands-free audio instructions that adapt to your pace and ability level"
    },
    {
        "icon": "📊",
        "title": "Smart Rep Counting & Scoring",
        "desc": "Accurate repetition tracking with confidence scoring for each movement"
    },
    {
        "icon": "💓",
        "title": "Real-Time Health Monitoring",
        "desc": "Heart rate tracking with automatic alerts and safety pauses when needed"
    },
    {
        "icon": "🏥",
        "title": "Telehealth Integration",
        "desc": "Direct connection to healthcare services with emergency location mapping"
    },
    {
        "icon": "♿",
        "title": "Inclusive Design",
        "desc": "Specialized support for wheelchair users and adaptive exercise routines"
    },
    {
        "icon": "🏆",
        "title": "Gamified Progress Tracking",
        "desc": "Leaderboards, achievements, and detailed analytics in SQLite database"
    },
    {
        "icon": "🔄",
        "title": "Auto-Pause Safety Feature",
        "desc": "Automatically pauses exercise when poor form or health risks are detected"
    }
]

for feature in features:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{feature['icon']}</div>
        <div class="feature-title">{feature['title']}</div>
        <div class="feature-desc">{feature['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close features-grid

# Healthcare Integration Section
st.markdown("""
<div class="healthcare-section">
    <h2 style="font-family: 'Oswald', sans-serif; font-size: 2.2rem; margin-bottom: 1rem;">
        🏥 FITNESS MEETS HEALTHCARE
    </h2>
    <p style="font-family: 'Roboto', sans-serif; font-size: 1.1rem; line-height: 1.6;">
        We're not just another fitness app. We're a <strong>health guardian</strong> that bridges the critical gap 
        between exercise and medical care. When our AI detects potential issues, it doesn't just warn you - 
        it connects you directly to professional help.
    </p>
</div>
""", unsafe_allow_html=True)

# Statistics Section
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <h2 style="font-family: 'Oswald', sans-serif; color: white; font-size: 2.2rem;">
        📈 BY THE NUMBERS
    </h2>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="stats-container">', unsafe_allow_html=True)

stats = [
    {"number": "90%+", "label": "Pose Detection Accuracy"},
    {"number": "0ms", "label": "Real-time Feedback Delay"},
    {"number": "8+", "label": "Supported Exercises"},
    {"number": "24/7", "label": "Health Monitoring"},
    {"number": "♿", "label": "Full Accessibility"},
    {"number": "🏥", "label": "Telehealth Ready"}
]

for stat in stats:
    st.markdown(f"""
    <div class="stat-item">
        <div class="stat-number">{stat['number']}</div>
        <div class="stat-label">{stat['label']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close stats-container

# Technology Stack
st.markdown("""
<div style="text-align: center; margin: 3rem 0;">
    <h2 style="font-family: 'Oswald', sans-serif; color: white; font-size: 2.2rem;">
        🛠 POWERED BY ADVANCED TECHNOLOGY
    </h2>
</div>
""", unsafe_allow_html=True)

tech_stack = ["MediaPipe Pose AI", "OpenCV", "Streamlit", "Python", "SQLite", "WebRTC", "pyttsx3", "Google Maps API",
              "Real-time Analytics"]

tech_html = "".join([f'<span class="tech-badge">{tech}</span>' for tech in tech_stack])
st.markdown(f'<div style="text-align: center; margin: 2rem 0;">{tech_html}</div>', unsafe_allow_html=True)

# Final Call to Action
st.markdown("""
<div style="text-align: center; background: rgba(255, 255, 255, 0.1); padding: 3rem; border-radius: 20px; margin: 3rem 0;">
    <h2 style="font-family: 'Montserrat', sans-serif; color: white; font-size: 2rem; margin-bottom: 1rem;">
        💪 JOIN THE FITNESS REVOLUTION
    </h2>
    <p style="font-family: 'Roboto', sans-serif; color: #E2E8F0; font-size: 1.2rem; line-height: 1.6;">
        Experience the future of safe, intelligent fitness where every workout is guided by AI 
        and protected by healthcare integration. <strong>Your safety is our priority.</strong>
    </p>
</div>
""", unsafe_allow_html=True)