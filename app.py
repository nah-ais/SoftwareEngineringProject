import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Nutrition Planner", page_icon="🔥", layout="wide")

# =====================================
# 1. LOAD DATASET (ROBUST)
# =====================================
BASE_DIR = Path(__file__).resolve().parent
local_csv = BASE_DIR / "food.csv"

def load_foods():
    if local_csv.exists():
        try:
            return pd.read_csv(local_csv)
        except:
            st.sidebar.error("Error loading foods.csv, using fallback dataset.")
    
    # fallback dataset
    return pd.DataFrame({
        "name": ["Chicken Breast (100g)", "Brown Rice (100g)", "Oatmeal (40g)", "Apple (1 medium)", "Egg (1pc)"],
        "calories": [165, 216, 150, 95, 78],
        "protein": [31, 5, 5, 0.5, 6],
        "carbs": [0, 45, 27, 25, 0.6],
        "fat": [3.6, 1.8, 2.5, 0.3, 5]
    })

df = load_foods()

# Storage for food logs (persists during session)
if "food_log" not in st.session_state:
    st.session_state.food_log = []


# =====================================
# 2. FUNCTIONS (CALCULATION)
# =====================================

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def get_activity_factor(activity):
    return {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Heavy": 1.725,
        "Athlete": 1.9
    }[activity]


def calculate_goal_calories(tdee, current_weight, goal_weight, days=None):
    if goal_weight == current_weight:
        return tdee
    
    diff = goal_weight - current_weight  # positif = naik, negatif = turun
    
    if days and days > 0:
        total_kcal = diff * 7700
        daily_adj = total_kcal / days
        return tdee + daily_adj
    
    if diff > 0:
        return tdee * 1.15
    return tdee * 0.85


# =====================================
# 3. UI HEADER (lebih estetis)
# =====================================

st.markdown("""
<h1 style="text-align:center; color:#333;">🔥 Personalized Nutrition Planner</h1>
<p style="text-align:center; font-size:18px;">Hitung kebutuhan kalori, input makanan, lihat grafik, dan dapatkan rekomendasi.</p>
""", unsafe_allow_html=True)


# =====================================
# 4. USER INFO FORM
# =====================================

st.subheader("📌 User Information")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])

with col2:
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    activity = st.selectbox("Activity Level", ["Sedentary", "Light", "Moderate", "Heavy", "Athlete"])

with col3:
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=60.0)


# =====================================
# 5. GOAL SETTINGS
# =====================================

st.subheader("🎯 Goal Settings")

goal_type = st.radio("Choose your goal:", ["Maintain Weight", "Lose Weight", "Gain Weight"])

goal_weight = weight
days = None

if goal_type != "Maintain Weight":
    goal_weight = st.number_input("Goal Weight (kg)", min_value=20.0, max_value=300.0, value=weight)
    days = st.number_input("Timeline (days) — optional", min_value=1, max_value=365, value=30)


# =====================================
# 6. CALCULATE BUTTON
# =====================================

if st.button("Calculate Daily Calorie Target"):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = bmr * get_activity_factor(activity)

    daily_calorie = calculate_goal_calories(
        tdee=tdee,
        current_weight=weight,
        goal_weight=goal_weight,
        days=days if goal_type != "Maintain Weight" else None
    )
    
    st.session_state.daily_goal = int(daily_calorie)

    # Card Display
    st.markdown(f"""
    <div style="padding:20px; border-radius:15px; background:#f0f2f6; text-align:center;">
        <h2>🔥 Daily Calorie Target: <b>{int(daily_calorie)} kcal / day</b></h2>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("See calculation details"):
        st.write(f"**BMR:** {round(bmr)} kcal")
        st.write(f"**TDEE:** {round(tdee)} kcal")
        st.write(f"**Goal Weight:** {goal_weight} kg")
        st.write(f"Timeline: {days} days" if days else "Using standard ±15% adjustment")


# =====================================
# 7. FOOD INPUT SYSTEM (FITUR 1)
# =====================================

st.subheader("🍽 Input Your Meals Today")

colA, colB = st.columns(2)

with colA:
    selected_food = st.selectbox("Select Food", df["name"].tolist())

with colB:
    grams = st.number_input("Amount (grams)", min_value=1, max_value=1000, value=100)

if st.button("Add to Daily Log"):
    food_row = df[df["name"] == selected_food].iloc[0]
    cal_per_gram = food_row["calories"] / 100
    total_cal = cal_per_gram * grams

    st.session_state.food_log.append({
        "name": selected_food,
        "grams": grams,
        "calories": round(total_cal)
    })

    st.success(f"Added {grams}g {selected_food} ({round(total_cal)} kcal)")


# Show log
if len(st.session_state.food_log) > 0:
    st.write("### 🍛 Today's Meals")

    food_df = pd.DataFrame(st.session_state.food_log)
    st.table(food_df)

    current_cal = food_df["calories"].sum()
else:
    current_cal = 0


# =====================================
# 8. CALORIE CHART (FITUR 2)
# =====================================
st.subheader("📊 Daily Calorie Progress")

if "daily_goal" in st.session_state:
    goal = st.session_state.daily_goal
else:
    goal = 2000  # default fallback

chart_df = pd.DataFrame({
    "Calories": [current_cal, goal],
}, index=["Consumed", "Goal"])

st.bar_chart(chart_df)


# =====================================
# 9. FOOD RECOMMENDATION
# =====================================

st.subheader("🥗 Food Recommendations (Low-calorie)")

recommended = df[df["calories"] <= 200].sample(min(3, len(df)))
st.dataframe(recommended)
