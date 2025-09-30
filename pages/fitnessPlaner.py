from __future__  import annotations
import streamlit as st
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import matplotlib.pyplot as plt

# ---------- Data classes ----------
@dataclass
class UserInput:
    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    bf_percent: float
    ssm_percent: Optional[float]
    pulse_bpm: Optional[int]
    activity_level: str
    diet_pref: str
    goal: str
    budget: str
    medical_conditions: List[str]

# ---------- Helper functions ----------
def safe_round(x: float, ndigits: int = 1) -> float:
    return round(x, ndigits)

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5: return "Underweight"
    if 18.5 <= bmi < 25.0: return "Normal"
    if 25.0 <= bmi < 30.0: return "Overweight"
    return "Obesity"

def bf_bucket_label(bf_percent: float) -> str:
    for start in range(0, 50, 5):
        end = start + 5
        if start <= bf_percent < end: return f"{start}-{end}%"
    return "50%+"

def bf_interpretation_by_sex(bf_percent: float, sex: str) -> str:
    s = sex.lower()
    if s == "male":
        if bf_percent < 6: return "Very low"
        if 6 <= bf_percent <= 13: return "Athlete/fit"
        if 14 <= bf_percent <= 17: return "Fitness"
        if 18 <= bf_percent <= 24: return "Average"
        return "High/Obese"
    else:
        if bf_percent < 14: return "Very low"
        if 14 <= bf_percent <= 20: return "Athlete/fit"
        if 21 <= bf_percent <= 24: return "Fitness"
        if 25 <= bf_percent <= 31: return "Average"
        return "High/Obese"

def ssm_interpretation(ssm_percent: Optional[float], sex: str) -> Optional[str]:
    if ssm_percent is None: return None
    s = sex.lower()
    if s == "male":
        if ssm_percent < 30: return "Low skeletal muscle %"
        if 30 <= ssm_percent <= 37: return "Average skeletal muscle %"
        return "High skeletal muscle %"
    else:
        if ssm_percent < 22: return "Low skeletal muscle %"
        if 22 <= ssm_percent <= 30: return "Average skeletal muscle %"
        return "High skeletal muscle %"

def mifflin_stjeor_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    s = sex.lower()
    if s == "male":
        return 10.0*weight_kg + 6.25*height_cm - 5.0*age + 5.0
    return 10.0*weight_kg + 6.25*height_cm - 5.0*age - 161.0

def activity_factor_for_level(level: str) -> float:
    return {"sedentary":1.2,"light":1.375,"moderate":1.55,"heavy":1.725}.get(level.lower(),1.2)

# ---------- Meal templates ----------
ICON_MAP = {"Breakfast":"🥣","Lunch":"🍱","Pre-workout":"⚡","Snack":"🍪","Dinner":"🍽","Note":"📝"}

def meal_templates_for(budget: str, diet: str):
    veg = [
        {"heading":"Breakfast","icon":ICON_MAP["Breakfast"],"text":"Greek yogurt + oats + fruit; or paneer bhurji.","price":"normal"},
        {"heading":"Pre-workout","icon":ICON_MAP["Pre-workout"],"text":"Banana + peanuts or small milkshake.","price":"normal"},
        {"heading":"Lunch","icon":ICON_MAP["Lunch"],"text":"Chickpea curry + brown rice/quinoa + salad.","price":"normal"},
        {"heading":"Snack","icon":ICON_MAP["Snack"],"text":"Almonds / roasted chana.","price":"normal"},
        {"heading":"Dinner","icon":ICON_MAP["Dinner"],"text":"Tofu/Paneer stir-fry + quinoa.","price":"normal"},
    ]
    nonveg = [
        {"heading":"Breakfast","icon":ICON_MAP["Breakfast"],"text":"3-egg omelette + oats with milk.","price":"normal"},
        {"heading":"Pre-workout","icon":ICON_MAP["Pre-workout"],"text":"Banana + whey/milk.","price":"normal"},
        {"heading":"Lunch","icon":ICON_MAP["Lunch"],"text":"Grilled chicken breast + sweet potato + salad.","price":"normal"},
        {"heading":"Snack","icon":ICON_MAP["Snack"],"text":"Greek yogurt / curd.","price":"normal"},
        {"heading":"Dinner","icon":ICON_MAP["Dinner"],"text":"Fish curry + brown rice + veg.","price":"normal"},
    ]
    if diet=="both":  # merge veg + non-veg
        base = veg + nonveg
    else:
        base = veg if diet=="veg" else nonveg
    for item in base:
        item["price_tag"] = {"budget":"💸 Budget-friendly","normal":"💰 Normal","premium":"💎 Premium"}.get(item.get("price","normal"))
    base.append({"heading":"Note","icon":ICON_MAP["Note"],"text":"High protein, balanced fats and carbs. Adjust portions to meet calorie/macro targets.","price_tag":""})
    return base

# ---------- Workout plan ----------
def generate_workout_plan(user: UserInput) -> Dict[str, List[Dict[str,str]]]:
    warmup = {"exercise":"Warm-up","sets_reps":"5-10 min","note":"Dynamic stretches & mobility."}
    cool = {"exercise":"Cool-down & stretch","sets_reps":"5-10 min","note":"Static stretching & breathing."}
    cardio = {"exercise":"Cardio","sets_reps":"20-40 min","note":"Brisk walk, cycling or HIIT."}
    chest_day = [{"exercise":"Push-ups / Bench Press","sets_reps":"3x8-12","note":""}]
    leg_day = [{"exercise":"Squats / Lunges","sets_reps":"3x8-12","note":""}]
    back_day = [{"exercise":"Rows / Pull-ups","sets_reps":"3x8-12","note":""}]
    full_body = [{"exercise":"Full-body circuit","sets_reps":"3 rounds","note":""}]
    core_finisher = [{"exercise":"Plank","sets_reps":"3x30-60s","note":""}]

    schedule = {"Monday":[],"Tuesday":[],"Wednesday":[],"Thursday":[],"Friday":[],"Saturday":[],"Sunday":[]}
    g = user.goal.lower()
    if g=="muscle_gain":
        schedule["Monday"] = [warmup]+chest_day+core_finisher+[cool]
        schedule["Tuesday"] = [warmup]+leg_day+core_finisher+[cool]
        schedule["Wednesday"] = [cardio]
        schedule["Thursday"] = [warmup]+back_day+core_finisher+[cool]
        schedule["Friday"] = [warmup]+full_body+[cool]
        schedule["Saturday"] = [cardio]
        schedule["Sunday"] = [{"exercise":"Active recovery","sets_reps":"30 min","note":"Yoga or mobility"}]
    else:
        schedule["Monday"] = [warmup]+full_body+[cardio]+core_finisher+[cool]
        schedule["Tuesday"] = [cardio]
        schedule["Wednesday"] = [warmup]+leg_day+core_finisher+[cool]
        schedule["Thursday"] = [cardio]
        schedule["Friday"] = [warmup]+chest_day+back_day+[cool]
        schedule["Saturday"] = [cardio]
        schedule["Sunday"] = [{"exercise":"Active recovery","sets_reps":"30 min","note":"Yoga or mobility"}]
    return schedule

# ---------- Streamlit App ----------
st.set_page_config(page_title="Gym Planner Pro", layout="wide")
st.title("🏋‍♂ Gym Planner Pro")

# ---------- Centered Form ----------
st.markdown("<h3 style='text-align: center;'>Enter Your Profile</h3>", unsafe_allow_html=True)
col_left, col_center, col_right = st.columns([1,2,1])

if 'user_input' not in st.session_state:
    st.session_state.user_input = None

with col_center:
    with st.form("user_form"):
        name = st.text_input("Name", value="John Doe")
        age = st.number_input("Age", 12, 80, 25)
        sex = st.selectbox("Sex", ["Male", "Female"])
        height_cm = st.number_input("Height (cm)", 120, 250, 170)
        weight_kg = st.number_input("Weight (kg)", 40, 200, 70)
        bf_percent = st.number_input("Body Fat %", 0.0, 60.0, 18.0)
        ssm_percent = st.number_input("Skeletal Muscle %", 0.0, 60.0, 35.0)
        pulse_bpm = st.number_input("Resting Pulse (bpm)", 40, 120, 70)
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Light", "Moderate", "Heavy"])
        diet_pref = st.selectbox("Diet Preference", ["veg", "non-veg","both"])
        goal = st.selectbox("Fitness Goal", ["Muscle_Gain", "Fat_Loss"])
        budget = st.selectbox("Budget Level", ["budget","normal","premium"])
        medical_conditions_options = [
            "Diabetes", "Hypertension", "Heart Disease", "Asthma", "Obesity",
            "Arthritis", "Cancer", "Kidney Disease", "Liver Disease", "Thyroid Disorders",
            "Anemia", "COPD", "Osteoporosis", "Migraine", "Sleep Apnea"
        ]
        medical_conditions_selected = st.multiselect(
            "Medical Conditions (select all that apply)",
            options=medical_conditions_options
        )
        submitted = st.form_submit_button("Generate Plan")

if submitted:
    st.session_state.user_input = UserInput(
        name=name, age=age, sex=sex, height_cm=height_cm, weight_kg=weight_kg,
        bf_percent=bf_percent, ssm_percent=ssm_percent, pulse_bpm=pulse_bpm,
        activity_level=activity_level, diet_pref=diet_pref.lower(),
        goal=goal.lower(), budget=budget, medical_conditions=medical_conditions_selected
    )

# ---------- Main Panel ----------
if st.session_state.user_input is not None:
    user = st.session_state.user_input

    # --- Health metrics ---
    bmi = safe_round(calculate_bmi(user.weight_kg, user.height_cm))
    bmi_class = classify_bmi(bmi)
    bf_label = bf_bucket_label(user.bf_percent)
    bf_interp = bf_interpretation_by_sex(user.bf_percent, user.sex)
    ssm_interp = ssm_interpretation(user.ssm_percent, user.sex)
    bmr = safe_round(mifflin_stjeor_bmr(user.weight_kg, user.height_cm, user.age, user.sex))
    tdee = safe_round(bmr * activity_factor_for_level(user.activity_level))

    st.subheader("📊 Your Health Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("BMI", f"{bmi} ({bmi_class})")
    col2.metric("Body Fat %", f"{user.bf_percent}% ({bf_interp})")
    col3.metric("Skeletal Muscle %", f"{user.ssm_percent}% ({ssm_interp})" if user.ssm_percent else "N/A")
    st.write(f"BMR: {bmr} kcal/day | TDEE: {tdee} kcal/day")
    st.write(f"Medical Conditions: {', '.join(user.medical_conditions) if user.medical_conditions else 'None'}")

    # --- Meal Plan ---
    st.subheader("🍽 Personalized Meal Plan")
    meals = meal_templates_for(user.budget, user.diet_pref)
    for meal in meals:
        st.markdown(f"{meal['icon']} {meal['heading']} {meal['price_tag']}: {meal['text']}")

    # --- Macro Pie Chart ---
    macros = {"Protein": 30, "Carbs": 45, "Fat": 25}  # Example split
    fig, ax = plt.subplots()
    ax.pie(macros.values(), labels=macros.keys(), autopct='%1.0f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # --- Workout Plan ---
    st.subheader("💪 Weekly Workout Plan")
    workout_plan = generate_workout_plan(user)
    days = list(workout_plan.keys())
    selected_day = st.selectbox("Select Day", days)
    st.write(f"*Exercises for {selected_day}:*")
    for ex in workout_plan[selected_day]:
        st.write(f"- {ex['exercise']} | {ex['sets_reps']} | {ex['note']}")

    # --- Export Options ---
    st.subheader("📁 Export Your Plan")
    plan_dict = {
        "profile": user.__dict__,
        "bmi": bmi, "bmi_class": bmi_class,
        "bf": user.bf_percent, "bf_interp": bf_interp,
        "ssm": user.ssm_percent, "ssm_interp": ssm_interp,
        "bmr": bmr, "tdee": tdee,
        "meals": meals,
        "workout_plan": workout_plan
    }
    json_str = json.dumps(plan_dict, indent=2)
    st.download_button("Download JSON Report", data=json_str, file_name=f"{user.name}_fitness_plan.json", mime="application/json")
    html_str = f"<h2>{user.name}'s Fitness Plan</h2><pre>{json_str}</pre>"
    st.download_button("Download HTML Report", data=html_str, file_name=f"{user.name}_fitness_plan.html", mime="text/html")