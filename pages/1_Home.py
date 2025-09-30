import streamlit as st
from streamlit_lottie import st_lottie
import requests
import base64

# Page Config
st.set_page_config(page_title="Health & Fitness", page_icon="💪", layout="wide")


# ---- Load Lottie Animation (Optional Fitness Animation) ----
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_fitness = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")


# ---- Background Image ----
def set_bg_img(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


set_bg_img(r"C:\Users\patel\PycharmProjects\Fitness\animations\img_1.png")

# ---- Custom Styling ----
st.markdown(
    """
    <style>
    .main-title {
        font-size: 52px;
        color: white;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
    }
    .sub-title {
        text-align: center;
        font-size: 20px;
        color: #ddd;
        margin-bottom: 30px;
    }
    .glass-box {
        background: rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 30px;
        margin: 20px auto;
        width: 85%;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        color: white;
    }
    .feature-box {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        margin: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .feature-box h4 {
        color: #F8C471;
        margin-bottom: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #bbb;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Title ----
st.markdown("<h1 class='main-title'>💪 Health & Fitness</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Your Personalized Fitness Platform for a Healthy Lifestyle 🧘‍♂️🏋️‍♀️</p>",
            unsafe_allow_html=True)

# ---- Intro Section ----
with st.container():
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_fitness:
            st_lottie(lottie_fitness, height=320, key="fitness")
    with col2:
        st.markdown(
            """
            ### 🏋️ Welcome to Health & Fitness  
            Begin your journey toward a **fitter, stronger, and healthier you**.  
            Explore personalized exercises, track progress, and stay consistent.

            💡 **Highlights:**
            - 🧘 Guided Workouts  
            - 🎯 Progress Tracking  
            - 🕒 Daily Goals  
            - 📅 Workout Planner  
            """
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Features Section ----
st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
st.markdown("### 🌟 Key Features", unsafe_allow_html=True)
colA, colB, colC = st.columns(3)

with colA:
    st.markdown(
        """
        <div class='feature-box'>
        <h4>🏋️ Guided Exercises</h4>
        <p>Follow workouts designed for strength, endurance, and flexibility.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with colB:
    st.markdown(
        """
        <div class='feature-box'>
        <h4>📊 Track Progress</h4>
        <p>Monitor your workout stats and track your improvements over time.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with colC:
    st.markdown(
        """
        <div class='feature-box'>
        <h4>🧠 Smart Recommendations</h4>
        <p>Get personalized tips based on your fitness goals and daily performance.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)

# ---- Getting Started ----
st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
st.markdown(
    """
    ### 🏁 Getting Started  
    1️⃣ Open **Exercise Page** from sidebar  
    2️⃣ Choose your workout (e.g. Yoga, Cardio, Strength)  
    3️⃣ Watch demo GIFs and follow along  
    4️⃣ Track your reps and sessions  
    5️⃣ Check your **Progress Dashboard** anytime  
    """
)
st.markdown("</div>", unsafe_allow_html=True)

# ---- Footer ----
st.markdown(
    "<p class='footer'>© 2025 Health & Fitness | Built with ❤️ using Streamlit</p>",
    unsafe_allow_html=True
)
