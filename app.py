import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="AI Health & Fitness Coach",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom HTML/CSS with more vibrant colors
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                   url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }

    .main-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 3rem;
        margin: 2rem;
        box-shadow: 0 25px 60px rgba(0,0,0,0.4);
        border: 2px solid rgba(255,255,255,0.3);
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.98));
    }

    .title-animation {
        font-size: 4.2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #FF6B35, #FF8E53, #4ECDC4, #45B7D1, #A363D9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        animation: glow 3s ease-in-out infinite alternate;
        background-size: 300% 300%;
        animation: gradientShift 4s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }

    @keyframes glow {
        from { 
            text-shadow: 0 0 25px rgba(255,107,53,0.6),
                        0 0 40px rgba(78,205,196,0.4),
                        0 0 60px rgba(163,99,217,0.3);
        }
        to { 
            text-shadow: 0 0 35px rgba(255,142,83,0.8),
                        0 0 50px rgba(69,183,209,0.6),
                        0 0 70px rgba(255,107,53,0.4);
        }
    }

    .welcome-text {
        font-size: 1.4rem;
        color: #FFFFFF;
        text-align: center;
        line-height: 1.7;
        margin-bottom: 2.5rem;
        background: linear-gradient(45deg, #FFFFFF, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 500;
    }

    .feature-list {
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2.5rem 0;
        border-left: 6px solid;
        border-image: linear-gradient(45deg, #FF6B35, #4ECDC4) 1;
        box-shadow: 0 15px 35px rgba(255,107,53,0.15);
    }

    .feature-item {
        padding: 1rem;
        margin: 0.8rem 0;
        background: rgba(255,255,255,0.9);
        border-radius: 12px;
        transition: all 0.4s ease;
        cursor: pointer;
        border-left: 4px solid transparent;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .feature-item:hover {
        transform: translateX(12px) scale(1.02);
        border-left: 4px solid;
        background: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .feature-item:nth-child(1):hover { border-left-color: #FF6B35; }
    .feature-item:nth-child(2):hover { border-left-color: #4ECDC4; }
    .feature-item:nth-child(3):hover { border-left-color: #45B7D1; }
    .feature-item:nth-child(4):hover { border-left-color: #A363D9; }
    .feature-item:nth-child(5):hover { border-left-color: #96CEB4; }

    .nav-button {
        background: linear-gradient(45deg, #FF6B35, #FF8E53, #4ECDC4);
        color: white;
        border: none;
        padding: 1.2rem 2.2rem;
        border-radius: 60px;
        margin: 0.6rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.4s ease;
        box-shadow: 0 8px 20px rgba(255,107,53,0.3);
        font-size: 1.1rem;
        background-size: 200% 200%;
        animation: buttonGlow 3s ease infinite;
    }

    @keyframes buttonGlow {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }

    .nav-button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 15px 35px rgba(255,107,53,0.5);
        background: linear-gradient(45deg, #FF8E53, #4ECDC4, #45B7D1);
    }

    .floating-element {
        animation: float 8s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-15px) rotate(1deg); }
        66% { transform: translateY(-8px) rotate(-1deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .stats-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.95));
        padding: 1.5rem;
        border-radius: 20px;
        transition: all 0.4s ease;
        cursor: pointer;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
    }

    .stats-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.6s ease;
    }

    .stats-card:hover::before {
        left: 100%;
    }

    .stats-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }

    .stats-card:nth-child(1):hover { border-color: #FF6B35; }
    .stats-card:nth-child(2):hover { border-color: #4ECDC4; }
    .stats-card:nth-child(3):hover { border-color: #45B7D1; }
    .stats-card:nth-child(4):hover { border-color: #A363D9; }
</style>
""", unsafe_allow_html=True)

# JavaScript for enhanced interactivity
components.html("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Enhanced click effects for feature items
    const features = document.querySelectorAll('.feature-item');
    features.forEach((feature, index) => {
        feature.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            this.style.background = 'linear-gradient(135deg, #FFFBEB, #FEF3C7)';
            setTimeout(() => {
                this.style.transform = 'translateX(12px) scale(1.02)';
                setTimeout(() => {
                    this.style.background = 'white';
                }, 300);
            }, 200);
        });
    });

    // Rainbow typing animation for title
    const title = document.querySelector('.title-animation');
    if (title) {
        const text = "🏋️ AI Health & Fitness Coach";
        title.innerHTML = '';
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                title.innerHTML += text.charAt(i);
                i++;
                // Change color for each character
                const chars = title.querySelectorAll('*');
                if (chars.length > 0) {
                    const lastChar = chars[chars.length - 1];
                    const colors = ['#FF6B35', '#FF8E53', '#4ECDC4', '#45B7D1', '#A363D9'];
                    lastChar.style.color = colors[i % colors.length];
                }
                setTimeout(typeWriter, 120);
            }
        }
        typeWriter();
    }

    // Particle effect on button hover
    const buttons = document.querySelectorAll('.nav-button');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.animation = 'buttonGlow 1.5s ease infinite';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.animation = 'buttonGlow 3s ease infinite';
        });
    });
});

// Add confetti effect on page load
function celebrate() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }
}

// Celebrate on first visit
if (!sessionStorage.getItem('celebrated')) {
    setTimeout(celebrate, 1000);
    sessionStorage.setItem('celebrated', 'true');
}
</script>

<!-- Include confetti library -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
""", height=0)

# Main content with vibrant colors
#st.markdown('<div class="main-container floating-element">', unsafe_allow_html=True)

# Animated title with rainbow effect
st.markdown('<h1 class="title-animation">🏋️ AI Health & Fitness Coach</h1>', unsafe_allow_html=True)


# Welcome text with gradient
st.markdown("""
<div class="welcome-text">
    <strong>Your intelligent fitness companion</strong> - Experience real-time AI coaching, 
    health monitoring, and personalized workouts in one powerful platform. 
    <span style="color: #FF6B35;">Transform your fitness journey</span> with cutting-edge technology!
</div>
""", unsafe_allow_html=True)

# Interactive navigation buttons with vibrant colors
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 Home", key="home_btn", use_container_width=True):
        st.switch_page("pages/1_Home.py")

with col2:
    if st.button("💪 Exercise", key="exercise_btn", use_container_width=True):
        st.switch_page("pages/2_Exercise.py")

with col3:
    if st.button("📊 Progress", key="progress_btn", use_container_width=True):
        st.switch_page("pages/3_Progress.py")

with col4:
    if st.button("🏥 Telehealth", key="telehealth_btn", use_container_width=True):
        st.switch_page("pages/4_TeleHealth.py")

with col5:
    if st.button("ℹ️ About", key="about_btn", use_container_width=True):
        st.switch_page("pages/5_About.py")

# Colorful separator
st.markdown("""
<div style="height: 4px; background: linear-gradient(45deg, #FF6B35, #FF8E53, #4ECDC4, #45B7D1); 
            border-radius: 2px; margin: 2rem 0;"></div>
""", unsafe_allow_html=True)

# Vibrant stats cards
st.markdown("### 📈 Quick Stats")
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

with stats_col1:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #FF6B35; margin: 0; font-size: 2.2rem;">5+</h3>
        <p style="margin: 0; color: #4A5568; font-weight: 600;">Active Users</p>
        <div style="height: 4px; background: linear-gradient(45deg, #FF6B35, #FF8E53); 
                    border-radius: 2px; margin-top: 0.5rem;"></div>
    </div>
    """, unsafe_allow_html=True)

with stats_col2:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #4ECDC4; margin: 0; font-size: 2.2rem;">99.2%</h3>
        <p style="margin: 0; color: #4A5568; font-weight: 600;">AI Accuracy</p>
        <div style="height: 4px; background: linear-gradient(45deg, #4ECDC4, #45B7D1); 
                    border-radius: 2px; margin-top: 0.5rem;"></div>
    </div>
    """, unsafe_allow_html=True)

with stats_col3:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #45B7D1; margin: 0; font-size: 2.2rem;">24/7</h3>
        <p style="margin: 0; color: #4A5568; font-weight: 600;">Monitoring</p>
        <div style="height: 4px; background: linear-gradient(45deg, #45B7D1, #A363D9); 
                    border-radius: 2px; margin-top: 0.5rem;"></div>
    </div>
    """, unsafe_allow_html=True)

with stats_col4:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #A363D9; margin: 0; font-size: 2.2rem;">100%</h3>
        <p style="margin: 0; color: #4A5568; font-weight: 600;">Safety Score</p>
        <div style="height: 4px; background: linear-gradient(45deg, #A363D9, #FF6B35); 
                    border-radius: 2px; margin-top: 0.5rem;"></div>
    </div>
    """, unsafe_allow_html=True)

# Demo section with colorful elements
st.markdown("""
<div style="height: 4px; background: linear-gradient(45deg, #A363D9, #96CEB4, #FF8E53); 
            border-radius: 2px; margin: 2rem 0;"></div>
""", unsafe_allow_html=True)

st.markdown("### 🎮 Try It Out")

# Colorful select box
demo_choice = st.selectbox(
    "What would you like to see?",
    ["AI Pose Detection", "Real-time Feedback", "Progress Tracking", "Safety Alerts"],
    key="demo_selector"
)


st.markdown('</div>', unsafe_allow_html=True)

# Enhanced sidebar with vibrant colors
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #FF6B35, #FF8E53, #A363D9); 
            color: white; padding: 1.8rem; border-radius: 20px; text-align: center;
            box-shadow: 0 15px 35px rgba(255,107,53,0.3); margin-bottom: 2rem;">
    <h3 style="margin: 0; font-size: 1.4rem;">🚀 Ready to Start?</h3>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Select a page to begin your fitness journey!</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.success("✅ **Select a page from the sidebar**")

# Colorful sidebar interactions
st.sidebar.markdown("### 💡 Quick Tips")
if st.sidebar.button("🎥 Enable Camera Access", use_container_width=True):
    st.sidebar.info("📸 **Camera enabled for AI analysis!**")

if st.sidebar.button("🔊 Test Audio Feedback", use_container_width=True):
    st.sidebar.success("🔊 **Audio feedback system working!**")

# Add confetti button for fun
if st.sidebar.button("🎉 Celebrate!", use_container_width=True):
    components.html("""
    <script>
    confetti({
        particleCount: 150,
        spread: 80,
        origin: { y: 0.6 }
    });
    </script>
    """, height=0)
    st.sidebar.balloons()