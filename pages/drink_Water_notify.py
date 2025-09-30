import streamlit as st
import datetime
import json
import os
import random
import plotly.express as px
from plyer import notification

# -----------------------------
# File to save hydration history
# -----------------------------
DATA_FILE = "water_data.json"

# -----------------------------
# Medical Conditions & Water Recommendations
# -----------------------------
MEDICAL_CONDITIONS = {
    "Normal Adult": {"min_l": 2.0, "max_l": 3.5},
    "Kidney Disease": {"min_l": 0.8, "max_l": 1.5},
    "Diabetes": {"min_l": 2.0, "max_l": 3.0},
    "Hypertension": {"min_l": 1.8, "max_l": 2.5},
    "Heart Condition (CHF)": {"min_l": 1.2, "max_l": 2.0},
    "Pregnancy": {"min_l": 2.8, "max_l": 3.8},
    "Breastfeeding": {"min_l": 3.0, "max_l": 4.0},
    "Kidney Stones Prevention": {"min_l": 3.0, "max_l": 4.0},
    "Fever/Diarrhea (rehydration)": {"min_l": 3.0, "max_l": 4.0},
    "Athlete / High Activity": {"min_l": 3.0, "max_l": 6.0},
    "Elderly (frail)": {"min_l": 1.5, "max_l": 2.0},
    "Custom": {"min_l": 2.0, "max_l": 3.5},
}

# -----------------------------
# Load / Save Functions
# -----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"history": {}, "streak": 0, "last_completed": None}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# -----------------------------
# Compute Daily Goal
# -----------------------------
def compute_goal(condition_key, weight=None, custom_min=None, custom_max=None):
    cond = MEDICAL_CONDITIONS.get(condition_key, MEDICAL_CONDITIONS["Normal Adult"])
    min_l = custom_min if condition_key == "Custom" and custom_min else cond["min_l"]
    max_l = custom_max if condition_key == "Custom" and custom_max else cond["max_l"]

    if weight and weight > 70:
        extra = (weight - 70) * 0.02
        min_l += extra
        max_l += extra

    target_l = (min_l + max_l) / 2.0
    return round(target_l, 2), round(min_l, 2), round(max_l, 2)

# -----------------------------
# Desktop Notification
# -----------------------------
def send_notification(message):
    try:
        notification.notify(
            title="💧 Water Reminder",
            message=message,
            timeout=5
        )
    except:
        pass

# -----------------------------
# Log Intake
# -----------------------------
def log_water(amount_l):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    today = str(datetime.date.today())
    if today not in data["history"]:
        data["history"][today] = []

    data["history"][today].append({"time": now, "amount_l": amount_l})

    total_today = sum(entry["amount_l"] for entry in data["history"][today])

    if total_today >= st.session_state["goal"]:
        yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        if data.get("last_completed") == yesterday:
            data["streak"] += 1
        elif data.get("last_completed") != today:
            data["streak"] = 1
        data["last_completed"] = today

    save_data(data)
    return total_today

# -----------------------------
# Delete Entry
# -----------------------------
def delete_entry(today, index):
    if today in data["history"]:
        data["history"][today].pop(index)
        if not data["history"][today]:
            del data["history"][today]
        save_data(data)
        st.session_state["refresh"] = not st.session_state.get("refresh", False)  # trigger rerun

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="💧 Medical Water Reminder", page_icon="💧", layout="centered")
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("C:/Users/patel/PycharmProjects/Fitness/animations/waterimage.jpg");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True
)
st.title("💧 Smart Medical-aware Water Reminder")
st.subheader("Track your hydration with real-time reminders & medical guidance")

# -----------------------------
# User Inputs
# -----------------------------
age = st.number_input("Enter Age", 10, 100, 30)
weight = st.number_input("Enter Weight (kg)", 30, 150, 70)
activity = st.selectbox("Activity Level", ["low", "moderate", "high"])
condition = st.selectbox("Medical Condition", list(MEDICAL_CONDITIONS.keys()))
custom_min, custom_max = None, None
if condition == "Custom":
    custom_min = st.number_input("Custom min (L)", 0.1, 20.0, 2.0, 0.1)
    custom_max = st.number_input("Custom max (L)", 0.1, 20.0, 3.5, 0.1)

if "goal" not in st.session_state:
    st.session_state["goal"] = 0.0
if "total" not in st.session_state:
    st.session_state["total"] = 0.0
if "refresh" not in st.session_state:
    st.session_state["refresh"] = False

if st.button("📌 Calculate Daily Water Goal"):
    st.session_state["goal"], min_l, max_l = compute_goal(condition, weight, custom_min, custom_max)
    st.session_state["total"] = 0.0
    st.success(f"✅ Your daily target: *{st.session_state['goal']} L* ({min_l}-{max_l} L recommended)")

# -----------------------------
# Intake Tracking
# -----------------------------
if st.session_state["goal"] > 0:
    st.markdown("### 🚰 Log Your Water Intake")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("250 ml"):
            st.session_state["total"] = log_water(0.25)
            send_notification("💧 Logged 250 ml water")
    with col2:
        if st.button("500 ml"):
            st.session_state["total"] = log_water(0.5)
            send_notification("💦 Logged 500 ml water")
    with col3:
        if st.button("1 L"):
            st.session_state["total"] = log_water(1.0)
            send_notification("🚰 Logged 1 L water")

    custom_amount = st.number_input("Custom intake (L)", 0.05, 10.0, 0.25, 0.05)
    if st.button("Log Custom Intake"):
        st.session_state["total"] = log_water(custom_amount)
        send_notification(f"💧 Logged {custom_amount} L water")

    progress = min(st.session_state["total"] / st.session_state["goal"], 1.0)
    st.progress(progress)
    st.info(f"💧 Today: {st.session_state['total']} L / {st.session_state['goal']} L")

    if st.session_state["total"] >= st.session_state["goal"]:
        st.balloons()
        st.success("🎉 Congratulations! You achieved your hydration goal today!")

    tips = [
        "Drink water before meals 🍽",
        "Hydration boosts skin ✨",
        "Dehydration affects focus 💡",
        "Sip regularly 🚰",
        "Stay hydrated 🌊"
    ]
    st.markdown(f"💡 Tip: {random.choice(tips)}")

# -----------------------------
# Weekly Report & Streaks (Attractive Graph)
# -----------------------------
st.markdown("### 📊 Weekly Hydration Report & Streaks")
daily_totals = {}
for day, entries in data["history"].items():
    daily_totals[day] = sum(entry.get("amount_l", 0) for entry in entries)

if daily_totals:
    last7 = sorted(daily_totals.items())[-7:]
    dates = [d for d, _ in last7]
    amounts = [a for _, a in last7]
    goal = st.session_state.get("goal", 2.5)

    fig = px.bar(
        x=dates,
        y=amounts,
        text=[f"{a:.2f} L" for a in amounts],
        labels={"x": "Date", "y": "Liters"},
        color=amounts,
        color_continuous_scale="Tealgrn",
        title="💧 Last 7 Days Hydration",
        height=400
    )

    fig.add_hline(
        y=goal,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Daily Goal ({goal} L)",
        annotation_position="top left"
    )

    fig.update_traces(
        textposition="outside",
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    )

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="Liters", showgrid=True, gridcolor='lightgrey')
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"🔥 Current streak: {data.get('streak', 0)} days")
else:
    st.write("No hydration history yet 🚰")

# -----------------------------
# Show today's detailed intake log with clear buttons
# -----------------------------
st.markdown("### 🕒 Today's Intake Log")
today = str(datetime.date.today())
if today in data["history"] and len(data["history"][today]) > 0:
    for i, entry in enumerate(data["history"][today]):
        col1, col2, col3 = st.columns([2, 2, 1])
        col1.write(entry["time"])
        col2.write(f"{entry['amount_l']} L")
        if col3.button("❌ Clear", key=f"clear_{i}"):
            delete_entry(today, i)
else:
    st.write("No intake logged today.")