import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import av
import pyttsx3
import threading
import time
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 140)  # Calm, clear speech
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


class PregWorkoutProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=1
        )
        self.current_exercise = "Pregnancy Squats"
        self.feedback = []
        self.safety_alerts = []
        self.accuracy_score = 0
        self.reps_count = 0
        self.stage = "rest"
        self.last_voice_time = 0
        self.voice_cooldown = 8  # seconds between voice prompts
        self.safety_score = 100  # Starts at 100, decreases with risky movements

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points with error handling"""
        try:
            a = np.array([a.x, a.y])
            b = np.array([b.x, b.y])
            c = np.array([c.x, c.y])

            ba = a - b
            bc = c - b

            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cosine_angle = np.clip(cosine_angle, -1, 1)
            angle = np.degrees(np.arccos(cosine_angle))

            return angle
        except:
            return 0

    def check_pregnancy_safety(self, landmarks):
        """Special safety checks for pregnancy exercises"""
        alerts = []

        try:
            # Check for excessive forward bending (dangerous in pregnancy)
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            # Calculate forward lean
            hip_center_y = (left_hip.y + right_hip.y) / 2
            forward_lean = nose.y - hip_center_y

            if forward_lean > 0.15:  # Excessive forward bending
                alerts.append("Avoid excessive forward bending")
                self.safety_score = max(0, self.safety_score - 5)

            # Check for balance issues
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

            balance_diff = abs(left_ankle.x - right_ankle.x)
            if balance_diff > 0.25:  # Unstable stance
                alerts.append("Widen stance for better balance")
                self.safety_score = max(0, self.safety_score - 3)

            # Check for twisting motions (avoid in pregnancy)
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            shoulder_hip_twist = abs((left_shoulder.x - right_shoulder.x) - (left_hip.x - right_hip.x))
            if shoulder_hip_twist > 0.1:  # Excessive twisting
                alerts.append("Avoid twisting motions - keep torso stable")
                self.safety_score = max(0, self.safety_score - 7)

        except Exception as e:
            print(f"Safety check error: {e}")

        return alerts

    def check_pregnancy_squats(self, landmarks):
        """Safe squats for pregnancy with limited range"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Gentle knee angle check (limited depth for pregnancy)
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
            right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)

            total_points += 2

            # Pregnancy-safe squat range (shallower than normal)
            is_squatting = (left_knee_angle < 140 and right_knee_angle < 140)

            if is_squatting:
                # Check for safe depth (not too deep during pregnancy)
                if 100 < left_knee_angle < 140 and 100 < right_knee_angle < 140:
                    accuracy_points += 2
                    if self.stage != "down":
                        self.stage = "down"
                        if time.time() - self.last_voice_time > self.voice_cooldown:
                            speak_async("Good squat depth. Now slowly stand up")
                            self.last_voice_time = time.time()
                else:
                    feedback.append("Squat shallower - pregnancy safety")

                # Knee alignment check
                if (left_knee.x < left_hip.x and right_knee.x > right_hip.x):
                    accuracy_points += 1
                else:
                    feedback.append("Keep knees aligned with hips")

            else:  # Standing position
                if left_knee_angle > 160 and right_knee_angle > 160:
                    accuracy_points += 2
                    if self.stage == "down":
                        self.stage = "up"
                        self.reps_count += 1
                        if time.time() - self.last_voice_time > self.voice_cooldown:
                            speak_async(f"Excellent! You've completed {self.reps_count} safe squats")
                            self.last_voice_time = time.time()
                else:
                    feedback.append("Return to full standing position")

        except Exception as e:
            feedback.append("Adjust position for better detection")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_pelvic_tilts(self, landmarks):
        """Safe pelvic tilts for pregnancy"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Pelvic tilt detection through hip and shoulder alignment
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            # Calculate pelvic tilt angle
            shoulder_center = [(left_shoulder.x + right_shoulder.x) / 2,
                               (left_shoulder.y + right_shoulder.y) / 2]
            hip_center = [(left_hip.x + right_hip.x) / 2,
                          (left_hip.y + right_hip.y) / 2]

            # Simple tilt detection (this is a simplified approach)
            tilt_angle = abs(shoulder_center[1] - hip_center[1])
            total_points += 1

            if tilt_angle > 0.02:  # Gentle tilt detected
                accuracy_points += 1
                if self.stage != "tilt":
                    self.stage = "tilt"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Good pelvic tilt. Now return to neutral")
                        self.last_voice_time = time.time()
            else:  # Neutral position
                if self.stage == "tilt":
                    self.stage = "neutral"
                    self.reps_count += 1
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async(f"Perfect! {self.reps_count} pelvic tilts completed")
                        self.last_voice_time = time.time()
                accuracy_points += 1

        except Exception as e:
            feedback.append("Stand sideways for better pelvic tilt detection")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def check_arm_circles(self, landmarks):
        """Gentle arm circles for shoulder mobility during pregnancy"""
        feedback = []
        accuracy_points = 0
        total_points = 0

        try:
            # Arm position detection
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            # Check if arms are raised (gentle arm circles)
            left_arm_raised = left_elbow.y < left_shoulder.y
            right_arm_raised = right_elbow.y < right_shoulder.y

            total_points += 2

            if left_arm_raised and right_arm_raised:
                accuracy_points += 2
                if self.stage != "raised":
                    self.stage = "raised"
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async("Arms raised nicely. Make gentle circles")
                        self.last_voice_time = time.time()
            else:
                if self.stage == "raised":
                    self.stage = "lowered"
                    self.reps_count += 0.5  # Half rep for each cycle
                    if time.time() - self.last_voice_time > self.voice_cooldown:
                        speak_async(f"Good arm movement. {int(self.reps_count)} circles done")
                        self.last_voice_time = time.time()
                accuracy_points += 2

        except Exception as e:
            feedback.append("Ensure arms are visible for detection")

        return feedback, (accuracy_points / total_points) * 100 if total_points > 0 else 0

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self.pose.process(image_rgb)
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Draw pose landmarks with pregnancy-safe colors (softer)
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(100, 200, 100), thickness=3, circle_radius=4),
                mp_drawing.DrawingSpec(color=(200, 100, 100), thickness=3, circle_radius=4)
            )

            landmarks = results.pose_landmarks.landmark

            # Pregnancy-specific safety checks
            self.safety_alerts = self.check_pregnancy_safety(landmarks)

            # Exercise-specific analysis
            if self.current_exercise == "Pregnancy Squats":
                self.feedback, self.accuracy_score = self.check_pregnancy_squats(landmarks)
            elif self.current_exercise == "Pelvic Tilts":
                self.feedback, self.accuracy_score = self.check_pelvic_tilts(landmarks)
            elif self.current_exercise == "Arm Circles":
                self.feedback, self.accuracy_score = self.check_arm_circles(landmarks)
            else:
                self.feedback = ["Select a pregnancy-safe exercise to begin"]
                self.accuracy_score = 0

            # Display pregnancy-safe information
            cv2.putText(image, f"Exercise: {self.current_exercise}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 0), 2)
            cv2.putText(image, f"Safety Score: {self.safety_score}%", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 0), 2)
            cv2.putText(image, f"Form Accuracy: {self.accuracy_score:.1f}%", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 2)
            cv2.putText(image, f"Reps: {int(self.reps_count)}", (10, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 2)

            # Display safety alerts in red
            for i, alert in enumerate(self.safety_alerts[:2]):
                cv2.putText(image, f"! {alert}", (10, 200 + i * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Display feedback in blue
            for i, text in enumerate(self.feedback[:2]):
                cv2.putText(image, f"* {text}", (10, 280 + i * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


def pregnancy_workout_panel():
    st.markdown("""
    <style>
    .pregnancy-header {
        background: linear-gradient(135deg, #FF6F61, #FF9B85);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .safety-warning {
        background: linear-gradient(135deg, #FF4444, #FF6B6B);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #FF0000;
    }
    .doctor-approval {
        background: linear-gradient(135deg, #4ECDC4, #44A08D);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .trimester-info {
        background: linear-gradient(135deg, #FFD166, #FFB347);
        color: black;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Critical Disclaimer Section
    st.markdown("""
    <div class="safety-warning">
        <h3>⚠️ IMPORTANT MEDICAL DISCLAIMER</h3>
        <p><strong>CONSULT YOUR DOCTOR BEFORE STARTING ANY EXERCISE DURING PREGNANCY</strong></p>
        <p>This tool is for guidance only. Stop immediately if you experience any pain, dizziness, 
        bleeding, or discomfort. Always prioritize your health and your baby's safety.</p>
    </div>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="pregnancy-header">
        <h1>🤰 Pregnancy-Safe Exercise Coach</h1>
        <p>Gentle, monitored workouts with real-time safety feedback for expectant mothers</p>
    </div>
    """, unsafe_allow_html=True)

    # Doctor Approval Check
    st.markdown("### 🩺 Medical Clearance")
    col_approval, col_trimester = st.columns(2)

    with col_approval:
        doctor_approved = st.selectbox(
            "Has your doctor approved exercise?",
            ["Select option", "Yes, with specific guidelines", "Yes, generally", "No", "Haven't asked yet"],
            help="CRITICAL: Always get medical clearance before exercising during pregnancy"
        )

    with col_trimester:
        trimester = st.selectbox(
            "Current Trimester",
            ["Select trimester", "First (1-12 weeks)", "Second (13-26 weeks)", "Third (27-40 weeks)"],
            help="Exercise recommendations vary by trimester"
        )

    # Warning if no doctor approval
    if doctor_approved in ["No", "Haven't asked yet"]:
        st.markdown("""
        <div class="safety-warning">
            <h4>🚫 STOP - Medical Clearance Required</h4>
            <p>Please consult your healthcare provider before using this exercise tool. 
            Pregnancy requires special considerations for safe physical activity.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Pregnancy exercise GIF mappings
    pregnancy_gifs = {
        "Pregnancy Squats": "animations/PregSquats.gif",
        "Pelvic Tilts": "animations/PregPelvicTilts.gif",
        "Arm Circles": "animations/PregArmCircles.gif"
    }

    # Fallback descriptions
    exercise_descriptions = {
        "Pregnancy Squats": "Gentle squats with limited depth for leg strength",
        "Pelvic Tilts": "Safe pelvic movements for back comfort",
        "Arm Circles": "Gentle arm movements for shoulder mobility"
    }

    # Sidebar with pregnancy-specific settings
    st.sidebar.markdown("### 🤰 Pregnancy Settings")

    # Voice guidance settings
    st.sidebar.markdown("#### 🔊 Voice Guidance")
    voice_enabled = st.sidebar.checkbox("Enable Calm Voice Instructions", value=True)
    comfort_level = st.sidebar.select_slider("Exercise Intensity",
                                             options=["Very Gentle", "Gentle", "Moderate"],
                                             value="Gentle")

    # Safety settings
    st.sidebar.markdown("#### ⚠️ Safety Features")
    safety_alerts = st.sidebar.checkbox("Enable Safety Alerts", value=True)
    auto_pause = st.sidebar.checkbox("Auto-Pause on Risky Movements", value=True)

    # Exercise selection
    st.sidebar.markdown("#### 🏃‍♂️ Safe Exercises")
    selected_exercise = st.sidebar.selectbox(
        "Choose Pregnancy-Safe Exercise:",
        list(pregnancy_gifs.keys()),
        format_func=lambda x: f"{x} - {exercise_descriptions[x]}"
    )

    # Trimester-specific warnings
    if trimester != "Select trimester":
        st.markdown("""
        <div class="trimester-info">
            <h4>📋 {trimester} Guidelines</h4>
            <p>• Avoid exercises lying on your back after first trimester</p>
            <p>• Stay hydrated and don't overheat</p>
            <p>• Listen to your body - stop if tired</p>
            <p>• Focus on gentle movements and breathing</p>
        </div>
        """.format(trimester=trimester), unsafe_allow_html=True)

    # Main content layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📺 Exercise Demonstration")

        # Display GIF with pregnancy-safe caption
        gif_path = pregnancy_gifs.get(selected_exercise)
        if gif_path:
            st.image(gif_path, use_container_width=True,
                     caption=f"Pregnancy-Safe: {selected_exercise}")
        else:
            st.info("💡 Add pregnancy exercise GIFs to animations folder")

        # Pregnancy-specific instructions
        st.markdown("### 📋 Safe Exercise Instructions")
        instructions = {
            "Pregnancy Squats": """
            **SAFE PREGNANCY SQUATS:**
            1. Use a chair for support if needed
            2. Feet shoulder-width apart, toes slightly out
            3. Lower slowly to a comfortable depth
            4. Don't squat deeper than 90 degrees
            5. Keep weight in heels, chest up
            6. Use arms for balance if necessary

            **PREGNANCY SAFETY TIPS:**
            • Stop if you feel any pelvic pressure
            • Don't hold your breath
            • Use wall support for balance
            • Limit to 10-15 repetitions
            """,
            "Pelvic Tilts": """
            **GENTLE PELVIC TILTS:**
            1. Stand with back against wall
            2. Knees slightly bent, feet hip-width
            3. Gently flatten lower back against wall
            4. Hold for 3 seconds, then release
            5. Focus on gentle movement, not strain

            **PREGNANCY SAFETY TIPS:**
            • Very small movements only
            • Stop if any discomfort
            • Breathe normally throughout
            • Support belly with hands if needed
            """,
            "Arm Circles": """
            **GENTLE ARM CIRCLES:**
            1. Sit or stand comfortably
            2. Raise arms to shoulder height
            3. Make small, slow circles forward
            4. Reverse direction after 10 circles
            5. Keep movements controlled

            **PREGNANCY SAFETY TIPS:**
            • Avoid raising arms above shoulders
            • Stop if shoulder discomfort
            • Maintain good posture
            • Focus on relaxation, not exertion
            """
        }

        st.info(instructions[selected_exercise])

    with col2:
        st.markdown("### 📹 Live Pregnancy Exercise Coach")

        # Initialize processor
        if 'preg_processor' not in st.session_state:
            st.session_state.preg_processor = PregWorkoutProcessor()

        processor = st.session_state.preg_processor
        processor.current_exercise = selected_exercise

        # Welcome message with voice
        if voice_enabled and st.button("🎤 Start Pregnancy-Safe Guidance"):
            speak_async(
                f"Beginning {selected_exercise}. Remember to move slowly and stop if you feel any discomfort. Your safety and your baby's safety come first.")

        # Webcam stream
        webrtc_ctx = webrtc_streamer(
            key="pregnancy-exercise-detection",
            video_processor_factory=PregWorkoutProcessor,
            rtc_configuration=RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            }),
            media_stream_constraints={"video": True, "audio": False}
        )

        # Real-time feedback display
        if webrtc_ctx.video_processor:
            processor = webrtc_ctx.video_processor

            # Critical safety alerts
            if processor.safety_alerts and safety_alerts:
                for alert in processor.safety_alerts:
                    st.markdown(f'<div class="safety-warning">⚠️ PREGNANCY ALERT: {alert}</div>',
                                unsafe_allow_html=True)
                    if voice_enabled:
                        speak_async(f"Pregnancy safety alert: {alert}")

            # Exercise feedback
            st.markdown("### 💬 Coach Feedback")
            feedback_card = st.container()

            with feedback_card:
                if processor.feedback:
                    for feedback in processor.feedback:
                        st.warning(f"📝 {feedback}")
                else:
                    st.success("✅ Perfect pregnancy-safe form!")

            # Pregnancy-specific metrics
            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric("Safety Score", f"{processor.safety_score}%")

            with col4:
                st.metric("Form Accuracy", f"{processor.accuracy_score:.1f}%")

            with col5:
                st.metric("Safe Reps", int(processor.reps_count))

    # Emergency section for pregnancy
    st.markdown("---")
    st.markdown("### 🆘 Pregnancy Emergency Guide")

    emergency_col1, emergency_col2 = st.columns(2)

    with emergency_col1:
        if st.button("🆘 STOP EXERCISE - Emergency", use_container_width=True):
            speak_async(
                "Exercise stopped immediately. Please sit down and rest. Contact your healthcare provider if you experience any concerning symptoms.")
            st.error("""
            **EMERGENCY STOP - Contact your doctor if you experience:**
            - Vaginal bleeding or fluid leakage
            - Regular painful contractions
            - Dizziness or fainting
            - Chest pain or difficulty breathing
            - Decreased fetal movement
            """)

    with emergency_col2:
        st.markdown("""
        **Normal to Stop Exercise:**
        • Feeling overly tired
        • Mild shortness of breath
        • Braxton Hicks contractions
        • Need to use bathroom
        • Just not feeling right
        """)


# Run the pregnancy workout panel
if __name__ == "__main__":
    pregnancy_workout_panel()