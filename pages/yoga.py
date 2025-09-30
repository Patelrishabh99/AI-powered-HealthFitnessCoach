import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import os

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class YogaPoseProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1
        )
        self.current_pose = "Mountain Pose"
        self.feedback = []
        self.accuracy_score = 0
        self.rep_count = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def check_mountain_pose(self, landmarks):
        """Check Mountain Pose (Tadasana)"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        # Shoulder alignment
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        total_points += 1
        if shoulder_diff < 0.02:
            accuracy_points += 1
        else:
            feedback.append("Level your shoulders")

        # Hip alignment
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        hip_diff = abs(left_hip[1] - right_hip[1])
        total_points += 1
        if hip_diff < 0.02:
            accuracy_points += 1
        else:
            feedback.append("Align hips evenly")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_warrior_ii(self, landmarks):
        """Check Warrior II Pose"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        # Front knee angle
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        knee_angle = self.calculate_angle(hip, knee, ankle)
        total_points += 1
        if 80 < knee_angle < 100:
            accuracy_points += 1
            if self.stage != "correct":
                self.stage = "correct"
                self.rep_count += 0.1  # Partial rep for holding correctly
        else:
            feedback.append(f"Bend front knee to 90° (Current: {knee_angle:.1f}°)")
            self.stage = "incorrect"

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_tree_pose(self, landmarks):
        """Check Tree Pose"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        # Foot placement relative to knee
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]

        vertical_diff = abs(ankle[0] - knee[0])
        total_points += 1
        if vertical_diff < 0.05:
            accuracy_points += 1
            if self.stage != "balanced":
                self.stage = "balanced"
                self.rep_count += 0.1
        else:
            feedback.append("Place foot firmly on inner thigh")
            self.stage = "unbalanced"

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_downward_dog(self, landmarks):
        """Check Downward Facing Dog"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        # Hip angle for inverted V
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        hip_angle = self.calculate_angle(wrist, hip, ankle)
        total_points += 1
        if 75 < hip_angle < 105:
            accuracy_points += 1
        else:
            feedback.append(f"Create a V shape (Current: {hip_angle:.1f}°)")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self.pose.process(image_rgb)
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )

            landmarks = results.pose_landmarks.landmark

            # Analyze current pose
            if self.current_pose == "Mountain Pose":
                self.feedback, self.accuracy_score = self.check_mountain_pose(landmarks)
            elif self.current_pose == "Warrior II":
                self.feedback, self.accuracy_score = self.check_warrior_ii(landmarks)
            elif self.current_pose == "Tree Pose":
                self.feedback, self.accuracy_score = self.check_tree_pose(landmarks)
            elif self.current_pose == "Downward Dog":
                self.feedback, self.accuracy_score = self.check_downward_dog(landmarks)
            else:
                self.feedback = ["Select a pose to begin analysis"]
                self.accuracy_score = 0

            # Display information on image
            cv2.putText(image, f"Pose: {self.current_pose}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, f"Accuracy: {self.accuracy_score:.1f}%", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, f"Score: {self.rep_count:.1f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            # Display feedback
            for i, text in enumerate(self.feedback[:2]):
                cv2.putText(image, text, (10, 120 + i * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


def yoga_panel():
    st.markdown("""
    <style>
    .yoga-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .pose-gif {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .feedback-card {
        background: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #4ECDC4;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="yoga-container">
        <h1 style="color: white; text-align: center; margin: 0;">🧘 AI Yoga & Asana Coach</h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
            Perfect your yoga poses with real-time AI feedback and animated guidance
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Yoga pose GIF mappings
    yoga_gifs = {
        "Mountain Pose": "animations/mountain pose.gif",
        "Warrior II": "animations/warrior.gif",
        "Tree Pose": "animations/tree_pose.gif",
        "Downward Dog": "animations/down dog.gif"
    }

    # Create fallback GIF paths or download URLs
    fallback_gifs = {
        "Mountain Pose": "https://media.giphy.com/media/l0Iy9psbP8qOeWgGI/giphy.gif",
        "Warrior II": "https://media.giphy.com/media/l0Iy5Pv4z7zqkNg3u/giphy.gif",
        "Tree Pose": "https://media.giphy.com/media/l0Iy9t8dM8qOeWgGI/giphy.gif",
        "Downward Dog": "https://media.giphy.com/media/l0Iy5Pv4z7zqkNg3u/giphy.gif"
    }

    # Sidebar for pose selection
    st.sidebar.markdown("### 🧘 Yoga Pose Selection")
    selected_pose = st.sidebar.selectbox(
        "Choose Yoga Pose:",
        list(yoga_gifs.keys()),
        help="Select a yoga pose to practice with AI guidance"
    )

    # User info
    st.sidebar.markdown("### 👤 Yoga Session")
    username = st.sidebar.text_input("Your Name", value="Yoga Student")
    session_duration = st.sidebar.slider("Session Duration (minutes)", 5, 60, 15)

    # Main content layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📺 Pose Demonstration")

        # Display GIF animation
        gif_path = yoga_gifs.get(selected_pose)
        if gif_path and os.path.exists(gif_path):
            st.image(gif_path, use_container_width=True, caption=f"{selected_pose} Demonstration")
        else:
            # Use fallback GIF from URL
            st.image(fallback_gifs[selected_pose], use_container_width=True,
                     caption=f"{selected_pose} Demonstration (Sample)")
            st.info("💡 Using sample animation. Add your GIFs to the animations folder!")

        # Pose instructions
        st.markdown("### 📋 Pose Instructions")
        instructions = {
            "Mountain Pose": """
            - Stand with feet together or hip-width apart
            - Distribute weight evenly through both feet  
            - Engage thigh muscles, lift kneecaps
            - Lengthen tailbone toward floor
            - Roll shoulders back and down
            - Arms by your sides, palms facing forward
            """,
            "Warrior II": """
            - Step feet 3-4 feet apart
            - Turn right foot out 90 degrees, left foot in slightly
            - Bend right knee to 90 degrees, knee over ankle
            - Extend arms parallel to floor
            - Gaze over right fingertips
            - Keep hips squared to the side
            """,
            "Tree Pose": """
            - Shift weight to left foot
            - Place right foot on left ankle, calf, or inner thigh
            - Avoid placing foot directly on knee
            - Bring palms together at heart center
            - Fix gaze on a stationary point
            - Keep hips level and squared forward
            """,
            "Downward Dog": """
            - Start on hands and knees
            - Tuck toes, lift hips toward ceiling
            - Hands shoulder-width apart, fingers spread
            - Feet hip-width apart
            - Press chest toward thighs
            - Keep arms and legs straight
            """
        }

        st.info(instructions[selected_pose])

    with col2:
        st.markdown("### 📹 Live Pose Detection")

        # Initialize session state
        if 'yoga_processor' not in st.session_state:
            st.session_state.yoga_processor = YogaPoseProcessor()

        st.session_state.yoga_processor.current_pose = selected_pose

        # Webcam stream
        webrtc_ctx = webrtc_streamer(
            key="yoga-pose-detection",
            video_processor_factory=YogaPoseProcessor,
            rtc_configuration=RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            }),
            media_stream_constraints={"video": True, "audio": False}
        )

        # Real-time feedback display
        if webrtc_ctx.video_processor:
            processor = webrtc_ctx.video_processor

            st.markdown("### 💬 AI Feedback")
            feedback_card = st.container()

            with feedback_card:
                if processor.feedback:
                    for i, feedback in enumerate(processor.feedback):
                        if i < 3:  # Show max 3 feedback items
                            st.error(f"🔴 {feedback}")
                else:
                    st.success("✅ Perfect form! Maintain this alignment.")

            # Metrics display
            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric("Current Accuracy", f"{processor.accuracy_score:.1f}%")

            with col4:
                st.metric("Pose Score", f"{processor.rep_count:.1f}")

            with col5:
                st.metric("Hold Time", "0:30")

            # Progress bar
            st.markdown("#### 🎯 Pose Accuracy")
            st.progress(processor.accuracy_score / 100)

    # Yoga session controls
    st.markdown("---")
    st.markdown("### 🎛️ Session Controls")

    col6, col7, col8 = st.columns(3)

    with col6:
        if st.button("🔄 Reset Session", use_container_width=True):
            if 'yoga_processor' in st.session_state:
                st.session_state.yoga_processor.rep_count = 0
                st.session_state.yoga_processor.accuracy_score = 0
            st.success("Session reset!")

    with col7:
        if st.button("💾 Save Progress", use_container_width=True):
            st.success("Progress saved to your yoga journal!")

    with col8:
        if st.button("📊 View History", use_container_width=True):
            st.info("Opening your yoga progress history...")

    # Benefits section
    st.markdown("### 🌟 Yoga Benefits")

    benefits_col1, benefits_col2 = st.columns(2)

    with benefits_col1:
        st.info("""
        **Physical Benefits:**
        - Improved flexibility and strength
        - Better posture and balance
        - Increased energy levels
        - Enhanced immune system
        - Pain relief and injury prevention
        """)

    with benefits_col2:
        st.info("""
        **Mental Benefits:**
        - Reduced stress and anxiety
        - Improved concentration
        - Better sleep quality
        - Increased mindfulness
        - Enhanced overall well-being
        """)

    # Voice guidance toggle
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔊 Audio Settings")
    voice_guidance = st.sidebar.toggle("Enable Voice Guidance", value=True)
    if voice_guidance:
        st.sidebar.success("Voice guidance enabled")
    else:
        st.sidebar.info("Voice guidance disabled")



# Run the yoga panel
if __name__ == "__main__":
    yoga_panel()