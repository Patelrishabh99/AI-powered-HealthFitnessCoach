import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import av
import pyttsx3
import threading
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import os
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Slower speech for clarity
engine.setProperty('volume', 0.8)


def speak_async(text):
    """Speak text asynchronously without blocking the main thread"""

    def speak():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=speak).start()


# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class SeniorExerciseProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,  # Lower confidence for flexibility
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        self.current_exercise = "Chair Squats"
        self.feedback = []
        self.safety_alerts = []
        self.accuracy_score = 0
        self.rep_count = 0
        self.stage = None
        self.last_voice_time = 0
        self.voice_cooldown = 5  # seconds between voice prompts

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points with safety checks"""
        try:
            a = np.array(a)
            b = np.array(b)
            c = np.array(c)

            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)

            if angle > 180.0:
                angle = 360 - angle

            return angle
        except:
            return 0

    def check_safety_limits(self, landmarks, exercise_type):
        """Check for movements that could be dangerous for seniors"""
        alerts = []

        # General safety checks for all exercises
        try:
            # Check for excessive bending
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

            bend_angle = self.calculate_angle(
                [nose[0], nose[1] + 0.1],  # Point above head
                nose,
                left_hip
            )

            if bend_angle > 45:  # Excessive forward bending
                alerts.append("Avoid bending too far forward")

            # Check balance stability
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            balance_diff = abs(left_ankle[0] - right_ankle[0])
            if balance_diff > 0.2:  # Unstable stance
                alerts.append("Widen stance for better balance")

        except Exception as e:
            print(f"Safety check error: {e}")

        return alerts

    def check_chair_squats(self, landmarks):
        """Safe chair squats for seniors"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Hip angle for squat depth
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            hip_angle = self.calculate_angle(shoulder, hip, knee)
            total_points += 1

            # Safe range for seniors (shallower squats)
            if 120 < hip_angle < 150:  # Partial squat range
                accuracy_points += 1
                if self.stage != "down":
                    self.stage = "down"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Good! Now slowly stand back up")
                        self.last_voice_time = time.time()
            elif hip_angle > 150:  # Standing position
                if self.stage == "down":
                    self.stage = "up"
                    self.rep_count += 1
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async(f"Excellent! You've completed {int(self.rep_count)} squats")
                        self.last_voice_time = time.time()
                accuracy_points += 1
            else:
                feedback.append("Don't squat too deep - keep it gentle")

        except Exception as e:
            feedback.append("Adjust your position for better detection")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_arm_raises(self, landmarks):
        """Gentle arm raises for shoulder mobility"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Arm angle for raising
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            arm_angle = self.calculate_angle(shoulder, elbow, wrist)
            total_points += 1

            # Safe arm raising range
            if arm_angle > 150:  # Arm raised
                accuracy_points += 1
                if self.stage != "up":
                    self.stage = "up"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Good lift! Now slowly lower your arm")
                        self.last_voice_time = time.time()
            else:  # Arm lowered
                if self.stage == "up":
                    self.stage = "down"
                    self.rep_count += 1
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async(f"Perfect! That's {int(self.rep_count)} arm raises")
                        self.last_voice_time = time.time()
                accuracy_points += 1

        except Exception as e:
            feedback.append("Make sure your arm is visible")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_leg_lifts(self, landmarks):
        """Seated or supported leg lifts"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Leg angle for lifting
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            leg_angle = self.calculate_angle(hip, knee, ankle)
            total_points += 1

            # Gentle leg lift range
            if 130 < leg_angle < 160:  # Leg lifted
                accuracy_points += 1
                if self.stage != "up":
                    self.stage = "up"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Nice leg lift! Hold for a moment")
                        self.last_voice_time = time.time()
            else:  # Leg down
                if self.stage == "up":
                    self.stage = "down"
                    self.rep_count += 1
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async(f"Great control! {int(self.rep_count)} leg lifts done")
                        self.last_voice_time = time.time()
                accuracy_points += 1

        except Exception as e:
            feedback.append("Adjust position for leg detection")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_neck_rotations(self, landmarks):
        """Gentle neck mobility exercises"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Head position relative to shoulders
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

            shoulder_center = [(left_shoulder[0] + right_shoulder[0]) / 2,
                               (left_shoulder[1] + right_shoulder[1]) / 2]

            head_offset = abs(nose[0] - shoulder_center[0])
            total_points += 1

            # Gentle neck rotation range
            if 0.05 < head_offset < 0.15:  # Head turned
                accuracy_points += 1
                if self.stage != "turned":
                    self.stage = "turned"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Good neck turn. Now slowly return to center")
                        self.last_voice_time = time.time()
            else:  # Head centered
                if self.stage == "turned":
                    self.stage = "center"
                    self.rep_count += 0.5  # Half rep for each side
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Excellent neck mobility")
                        self.last_voice_time = time.time()
                accuracy_points += 1

        except Exception as e:
            feedback.append("Face the camera for neck exercise")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self.pose.process(image_rgb)
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Draw pose landmarks with senior-friendly colors (softer)
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(100, 200, 100), thickness=3, circle_radius=4),
                mp_drawing.DrawingSpec(color=(200, 100, 100), thickness=3, circle_radius=4)
            )

            landmarks = results.pose_landmarks.landmark

            # Safety checks first
            self.safety_alerts = self.check_safety_limits(landmarks, self.current_exercise)

            # Exercise-specific analysis
            if self.current_exercise == "Chair Squats":
                self.feedback, self.accuracy_score = self.check_chair_squats(landmarks)
            elif self.current_exercise == "Arm Raises":
                self.feedback, self.accuracy_score = self.check_arm_raises(landmarks)
            elif self.current_exercise == "Leg Lifts":
                self.feedback, self.accuracy_score = self.check_leg_lifts(landmarks)
            elif self.current_exercise == "Neck Rotations":
                self.feedback, self.accuracy_score = self.check_neck_rotations(landmarks)
            else:
                self.feedback = ["Select an exercise to begin"]
                self.accuracy_score = 0

            # Display senior-friendly information
            cv2.putText(image, f"Exercise: {self.current_exercise}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 0), 2)
            cv2.putText(image, f"Safety Score: {self.accuracy_score:.1f}%", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 0), 2)
            cv2.putText(image, f"Reps: {int(self.rep_count)}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 2)

            # Display safety alerts in red
            for i, alert in enumerate(self.safety_alerts[:2]):
                cv2.putText(image, f"! {alert}", (10, 160 + i * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Display feedback in blue
            for i, text in enumerate(self.feedback[:2]):
                cv2.putText(image, f"* {text}", (10, 240 + i * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


def senior_exercise_panel():
    st.markdown("""
    <style>
    .senior-container {
        background: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .safety-alert {
        background: linear-gradient(135deg, #ff6b6b, #ff8e53);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ff4444;
    }
    .voice-guide {
        background: linear-gradient(135deg, #4ECDC4, #44A08D);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .large-text {
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header with senior-friendly design
    st.markdown("""
    <div class="senior-container">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">👵 Senior-Friendly Exercise Coach</h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Safe, gentle exercises with voice guidance and injury prevention
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Senior exercise GIF mappings
    senior_gifs = {
        "Chair Squats": "animations/chairSqarts.gif",
        "Arm Raises": "animations/armraises.gif",
        "Leg Lifts": "animations/SeatedLegRaise.gif",
        "Neck Rotations": "animations/senior_neck_rotations.gif"
    }

    # Fallback GIF URLs for seniors
    fallback_gifs = {
        "Chair Squats": "https://media.giphy.com/media/l0Iy9psbP8qOeWgGI/giphy.gif",
        "Arm Raises": "https://media.giphy.com/media/l0Iy5Pv4z7zqkNg3u/giphy.gif",
        "Leg Lifts": "https://media.giphy.com/media/l0Iy9t8dM8qOeWgGI/giphy.gif",
        "Neck Rotations": "https://media.giphy.com/media/l0Iy5Pv4z7zqkNg3u/giphy.gif"
    }

    # Sidebar with large, clear controls
    st.sidebar.markdown("### 👴 Senior Exercise Settings")

    # Voice guidance settings
    st.sidebar.markdown("#### 🔊 Voice Guidance")
    voice_enabled = st.sidebar.checkbox("Enable Voice Instructions", value=True)
    voice_speed = st.sidebar.select_slider("Speech Speed", options=["Slow", "Medium", "Fast"], value="Medium")

    # Safety settings
    st.sidebar.markdown("#### ⚠️ Safety Settings")
    safety_alerts = st.sidebar.checkbox("Enable Safety Alerts", value=True)
    max_difficulty = st.sidebar.selectbox("Maximum Difficulty", ["Very Gentle", "Gentle", "Moderate"], index=0)

    # Exercise selection with senior-friendly descriptions
    st.sidebar.markdown("#### 🏃 Exercise Selection")
    selected_exercise = st.sidebar.selectbox(
        "Choose Exercise:",
        list(senior_gifs.keys()),
        format_func=lambda x: {
            "Chair Squats": "Chair Squats - Safe sitting/standing",
            "Arm Raises": "Arm Raises - Shoulder mobility",
            "Leg Lifts": "Leg Lifts - Seated leg exercises",
            "Neck Rotations": "Neck Rotations - Gentle neck moves"
        }[x]
    )

    # Main content layout with large, clear sections
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📺 Exercise Demonstration")

        # Display GIF with large caption
        gif_path = senior_gifs.get(selected_exercise)
        if gif_path and os.path.exists(gif_path):
            st.image(gif_path, use_container_width=True)
        else:
            st.image(fallback_gifs[selected_exercise], use_container_width=True)
            st.info("💡 Using sample animation. Add senior exercise GIFs to animations folder!")

        # Large, clear instructions
        st.markdown("### 📋 Step-by-Step Instructions")
        instructions = {
            "Chair Squats": """
            **SAFE CHAIR SQUATS:**
            1. Sit on a sturdy chair with feet flat
            2. Hold onto chair arms for support
            3. Slowly stand up without using hands
            4. Pause for 2 seconds at the top
            5. Slowly sit back down with control
            6. Repeat 5-10 times gently

            **SAFETY TIPS:**
            • Always have support nearby
            • Don't squat too deep
            • Stop if you feel dizzy
            """,
            "Arm Raises": """
            **GENTLE ARM RAISES:**
            1. Sit or stand comfortably
            2. Start with arms at your sides
            3. Slowly raise arms to shoulder height
            4. Hold for 3 seconds at the top
            5. Slowly lower arms back down
            6. Repeat 8-12 times per side

            **SAFETY TIPS:**
            • Don't raise above shoulder height
            • Move slowly and controlled
            • Stop if shoulder pain occurs
            """,
            "Leg Lifts": """
            **SEATED LEG LIFTS:**
            1. Sit on a chair with back straight
            2. Hold onto seat for balance
            3. Slowly lift one leg straight out
            4. Hold for 3 seconds at the top
            5. Slowly lower leg back down
            6. Alternate legs, 5-10 each side

            **SAFETY TIPS:**
            • Keep back supported
            • Don't lift too high
            • Move slowly to avoid strain
            """,
            "Neck Rotations": """
            **GENTLE NECK MOVES:**
            1. Sit upright with shoulders relaxed
            2. Slowly turn head to look left
            3. Hold for 3 seconds, return to center
            4. Slowly turn head to look right
            5. Hold for 3 seconds, return to center
            6. Repeat 5 times each direction

            **SAFETY TIPS:**
            • Never force the movement
            • Stop immediately if dizzy
            • Keep movements very small
            """
        }

        st.markdown(f'<div class="large-text">{instructions[selected_exercise]}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 📹 Live Exercise Coach")

        # Initialize session state
        if 'senior_processor' not in st.session_state:
            st.session_state.senior_processor = SeniorExerciseProcessor()

        processor = st.session_state.senior_processor
        processor.current_exercise = selected_exercise

        # Welcome voice message
        if voice_enabled and st.button("🎤 Start Voice Guidance"):
            speak_async(
                f"Welcome to senior exercises. Let's begin with {selected_exercise}. Remember to move slowly and safely.")

        # Webcam stream
        webrtc_ctx = webrtc_streamer(
            key="senior-exercise-detection",
            video_processor_factory=SeniorExerciseProcessor,
            rtc_configuration=RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            }),
            media_stream_constraints={"video": True, "audio": False}
        )

        # Real-time feedback display
        if webrtc_ctx.video_processor:
            processor = webrtc_ctx.video_processor

            # Safety alerts (high priority)
            if processor.safety_alerts and safety_alerts:
                for alert in processor.safety_alerts:
                    st.markdown(f'<div class="safety-alert">⚠️ {alert}</div>', unsafe_allow_html=True)
                    if voice_enabled:
                        speak_async(f"Safety alert: {alert}")

            # Exercise feedback
            st.markdown("### 💬 Coach Feedback")
            feedback_card = st.container()

            with feedback_card:
                if processor.feedback:
                    for feedback in processor.feedback:
                        st.warning(f"📝 {feedback}")
                else:
                    st.success("✅ Perfect form! You're doing great!")

            # Senior-friendly metrics
            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric("Safety Score", f"{processor.accuracy_score:.1f}%")

            with col4:
                st.metric("Reps Completed", int(processor.rep_count))

            with col5:
                st.metric("Exercise Time", "2:30")

            # Progress with large, clear display
            st.markdown("#### 🎯 Session Progress")
            st.progress(processor.accuracy_score / 100)

    # Senior-specific features section
    st.markdown("---")
    st.markdown("### 🌟 Special Senior Features")

    senior_col1, senior_col2, senior_col3 = st.columns(3)

    with senior_col1:
        st.markdown("""
        <div class="voice-guide">
            <h4>🎤 Voice Guidance</h4>
            <p>Step-by-step audio instructions</p>
            <p>Clear, slow pronunciation</p>
            <p>Safety reminders</p>
        </div>
        """, unsafe_allow_html=True)

    with senior_col2:
        st.markdown("""
        <div class="safety-alert">
            <h4>🛡️ Safety First</h4>
            <p>Injury prevention alerts</p>
            <p>Gentle movement detection</p>
            <p>Emergency stop guidance</p>
        </div>
        """, unsafe_allow_html=True)

    with senior_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #96CEB4, #88C9A1); color: white; padding: 1rem; border-radius: 15px;">
            <h4>💙 Senior Designed</h4>
            <p>Large, clear text</p>
            <p>Simple controls</p>
            <p>Accessible interface</p>
        </div>
        """, unsafe_allow_html=True)

    # Emergency and help section
    st.markdown("### 🆘 Safety & Help")

    help_col1, help_col2 = st.columns(2)

    with help_col1:
        if st.button("🆘 Emergency Stop", use_container_width=True):
            speak_async("Exercise stopped immediately. Please sit down and rest. Help is available if needed.")
            st.error("EMERGENCY STOP: Exercise paused. Rest and seek help if needed.")

    with help_col2:
        if st.button("📞 Call for Help", use_container_width=True):
            st.warning("Emergency contact feature would connect to caregiver or medical help")
            speak_async("Help has been notified. Please remain calm and seated.")


# Setup senior animations folder
def setup_senior_animations():
    """Create animations folder for senior exercises"""
    anim_dir = "animations"
    if not os.path.exists(anim_dir):
        os.makedirs(anim_dir)

    senior_anim_files = [
        "senior_chair_squats.gif", "senior_arm_raises.gif",
        "senior_leg_lifts.gif", "senior_neck_rotations.gif"
    ]

    return anim_dir


# Run the setup
setup_senior_animations()

# Run the senior exercise panel
if __name__ == "__main__":
    senior_exercise_panel()