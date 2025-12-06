import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Nutrition Planner", page_icon="🔥", layout="centered")

# ============================
# 1. LOAD DATASET (ROBUST)
# ============================
BASE_DIR = Path(__file__).resolve().parent
local_csv = BASE_DIR / "food.csv"

def load_foods():
    if local_csv.exists():
        try:
            df = pd.read_csv(local_csv)
            return df
        except:
            st.sidebar.error("Error reading foods.csv. Using fallback dataset.")
    
    # Fallback dataset
    sample_data = {
        "name": [
            "Chicken Breast (100g)", "Brown Rice (100g)", "Oatmeal (40g)",
            "Greek Yogurt (100g)", "Whole Egg (1pc)", "Apple (1 medium)"
        ],
        "calories": [165, 216, 150, 59, 78, 95],
        "protein": [31, 5, 5, 10, 6, 0.5],
        "carbs": [0, 45, 27, 3.6, 0.6, 25],
        "fat": [3.6, 1.8, 2.5, 0.4, 5, 0.3]
    }
    return pd.DataFrame(sample_data)


df = load_foods()


# ============================
# 2. FUNCTIONS (BMR, TDEE, GOAL)
# ============================

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def get_activity_factor(activity):
    factors = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Heavy": 1.725,
        "Athlete": 1.9
    }
    return factors[activity]


def calculate_goal_calories(tdee, current_weight, goal_weight, days=None):
    if goal_weight == current_weight:
        return tdee
    
    diff = goal_weight - current_weight  # + naik, - turun

    if days and days > 0:
        total_kcal = diff * 7700
        daily_adjustment = total_kcal / days
        return tdee + daily_adjustment

    if diff > 0:
        return tdee * 1.15
    else:
        return tdee * 0.85


# ============================
# 3. STREAMLIT UI
# ============================

st.title("🔥 Personalized Nutrition Planner")
st.write("Hitung kebutuhan kalori harian + rekomendasi makanan.")

st.header("📌 User Information")

# User Inputs
age = st.number_input("Age", min_value=1, max_value=120, value=25)
height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=60.0)
gender = st.selectbox("Gender", ["Male", "Female"])
activity = st.selectbox("Activity Level", ["Sedentary", "Light", "Moderate", "Heavy", "Athlete"])


# ============================
# 4. GOAL & TIMELINE
# ============================
st.header("🎯 Goal Settings")

goal_type = st.selectbox("Choose your goal:", ["Maintain Weight", "Lose Weight", "Gain Weight"])

goal_weight = weight
days = None

if goal_type != "Maintain Weight":
    goal_weight = st.number_input("Goal Weight (kg)", min_value=20.0, max_value=300.0, value=weight)
    days = st.number_input("Timeline (days) – optional", min_value=1, max_value=365, value=30)


# ============================
# 5. CALCULATION BUTTON
# ============================
if st.button("Calculate My Daily Calories"):
    # Step 1: BMR
    bmr = calculate_bmr(weight, height, age, gender)

    # Step 2: TDEE
    tdee = bmr * get_activity_factor(activity)

    # Step 3: Final Calorie Target
    daily_calorie = calculate_goal_calories(
        tdee=tdee,
        current_weight=weight,
        goal_weight=goal_weight,
        days=days if goal_type != "Maintain Weight" else None
    )

    st.success(f"🔥 Your Daily Calorie Target: **{int(daily_calorie)} kcal/day**")

    # details
    with st.expander("See calculation details"):
        st.write(f"**BMR:** {round(bmr)} kcal/day")
        st.write(f"**TDEE:** {round(tdee)} kcal/day")
        st.write(f"**Goal Weight:** {goal_weight} kg")
        if days:
            st.write(f"**Timeline:** {days} days")
        else:
            st.write("Using standard ±15% method (no timeline).")

    # ============================
    # 6. FOOD RECOMMENDATION
    # ============================
    st.header("🥗 Food Recommendations")

    recommended = df[df["calories"] <= 300].sample(min(3, len(df)))

    st.write("Based on low-calorie foods (<300 kcal):")
    st.dataframe(recommended)



# ============================
# END OF APP
# ============================

