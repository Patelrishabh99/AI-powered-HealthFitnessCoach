import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import sqlite3
import os
import random
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

# ------------------- Page Setup -------------------
st.set_page_config(page_title="AI Health & Fitness Coach", layout="wide")
st.title("🏋️ AI Health & Fitness Coach")
st.write("Interactive AI fitness platform: posture correction, reps counting, heart-rate monitoring, gamification, and telehealth alerts.")

# ------------------- Voice Engine -------------------
engine = pyttsx3.init()
engine.setProperty("rate", 160)
def speak_async(text):
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait()).start()

# ------------------- MediaPipe Pose -------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# ------------------- Database -------------------
if not os.path.exists("data"):
    os.makedirs("data")
conn = sqlite3.connect("data/user_logs.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    exercise TEXT,
    reps INTEGER,
    date TEXT
)
""")
conn.commit()

def save_progress(username, exercise, reps):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO user_progress (username, exercise, reps, date) VALUES (?, ?, ?, ?)",
              (username, exercise, reps, date))
    conn.commit()

def get_leaderboard():
    df = st.cache_data(lambda:
        pd.read_sql_query("""
            SELECT username, SUM(reps) as total_reps 
            FROM user_progress 
            GROUP BY username 
            ORDER BY total_reps DESC
        """, conn)
    )()
    return df

# ------------------- Helper Functions -------------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# ------------------- Sidebar -------------------
username = st.sidebar.text_input("Enter Your Name", value="Guest")
exercise = st.sidebar.selectbox("Select Exercise", ["Bicep Curl", "Squat", "Push-up", "Shoulder Press", "Special Needs"])

# Heart Rate simulation
heart_rate = random.randint(70, 130)
st.sidebar.metric(label="Heart Rate (BPM)", value=heart_rate)
if heart_rate > 110:
    st.sidebar.warning("⚠️ High Heart Rate! Slow down or pause exercise!")
    st.sidebar.markdown("[Find Nearby Clinics](https://www.google.com/maps/search/clinic/)")

# Exercise GIF mapping
exercise_gifs = {
    "Bicep Curl": "animations/bisep.gif",
    "Squat": "animations/How To Do Perform Jump Squat _ Form, Tips And Benefits.gif",
    "Push-up": "animations/7146402d-2b40-4be6-b1ed-6a870e1201ab.gif",
    "Shoulder Press": "animations/download.gif",
    "Special Needs": "animations/Cardio exercises for disabled.jpg"
}

# ------------------- Pose & Coaching -------------------
class PoseCoach(VideoTransformerBase):
    rep_count = 0
    stage = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        height, width, _ = img.shape
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        feedback = ""
        confidence = 0

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            confidence = np.mean([lmk.visibility for lmk in landmarks])*100

            # Draw skeleton
            for connection in mp_pose.POSE_CONNECTIONS:
                start_idx, end_idx = connection
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                x1, y1 = int(start.x * width), int(start.y * height)
                x2, y2 = int(end.x * width), int(end.y * height)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3, cv2.LINE_AA)

            # ----------------- Exercise Logic -----------------
            if exercise == "Bicep Curl":
                shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    self.stage = "down"
                    speak_async("Lower your arm")
                if angle < 50 and self.stage == "down":
                    self.stage = "up"
                    self.rep_count += 1
                    speak_async("Good job! One rep completed!")

                feedback = "Curl your arm!" if angle > 160 else ("Keep curling!" if angle < 50 else "Perfect!")

            elif exercise == "Squat":
                hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                angle = calculate_angle(hip, knee, ankle)

                if angle > 160:
                    self.stage = "up"
                    speak_async("Stand tall")
                if angle < 90 and self.stage == "up":
                    self.stage = "down"
                    self.rep_count += 1
                    speak_async("Great! One squat done!")

                feedback = "Go deeper!" if angle < 90 else ("Stand tall!" if angle > 160 else "Good posture!")

            elif exercise == "Push-up":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    self.stage = "up"
                    speak_async("Push up")
                if angle < 90 and self.stage == "up":
                    self.stage = "down"
                    self.rep_count += 1
                    speak_async("Push-up done!")

                feedback = "Go down!" if angle < 90 else ("Push up!" if angle > 160 else "Good!")

            elif exercise == "Shoulder Press":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                angle = calculate_angle(shoulder, elbow, wrist)

                if angle < 90:
                    self.stage = "down"
                    speak_async("Lower down")
                if angle > 160 and self.stage == "down":
                    self.stage = "up"
                    self.rep_count += 1
                    speak_async("One shoulder press done!")

                feedback = "Push up!" if angle > 160 else ("Lower down!" if angle < 90 else "Good posture!")

            elif exercise == "Special Needs":
                feedback = "Gentle movements, lift your arms slowly"
                speak_async(feedback)

            # Overlay info
            cv2.putText(img, f"{feedback}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.putText(img, f"Reps: {self.rep_count}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.putText(img, f"Confidence: {confidence:.1f}%", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

        return img

# ------------------- Layout -------------------
import pandas as pd
col1, col2 = st.columns([1,1])

with col1:
    gif_path = exercise_gifs.get(exercise, None)
    if gif_path and os.path.exists(gif_path):
        st.image(gif_path, use_column_width=True)
    else:
        st.write("Animation not found!")

with col2:
    rtc_configuration = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    webrtc_streamer(
        key="fitness_coach",
        video_transformer_factory=PoseCoach,
        rtc_configuration=rtc_configuration
    )

# ------------------- Gamification -------------------
st.subheader("🏆 Save Your Progress / Leaderboard")
if st.button("Save Session Progress"):
    transformer = st.session_state.get("pose_transformer")
    reps = transformer.rep_count if transformer else 0
    save_progress(username, exercise, reps)
    st.success(f"Saved {reps} reps for {username}!")

leaderboard = pd.read_sql_query("SELECT username, SUM(reps) as total_reps FROM user_progress GROUP BY username ORDER BY total_reps DESC", conn)
st.dataframe(leaderboard)