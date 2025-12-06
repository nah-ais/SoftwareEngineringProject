import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calorie Prototype", page_icon="🔥")

# Load simple dataset
df = pd.read_csv("food.csv")

st.title("🔥 Daily Calorie Intake Prototype")
st.write("Prototype sederhana untuk menghitung kebutuhan kalori dan rekomendasi makanan.")

# ==============================
# 1. USER INPUT
# ==============================
st.header("📌 Input Your Data")

age = st.number_input("Age", min_value=1, max_value=100)
height = st.number_input("Height (cm)", min_value=50, max_value=250)
weight = st.number_input("Weight (kg)", min_value=20, max_value=300)
gender = st.selectbox("Gender", ["Male", "Female"])
activity = st.selectbox(
    "Activity Level",
    ["Sedentary", "Light", "Moderate", "Heavy", "Athlete"]
)

# Activity factors
activity_factor = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Heavy": 1.725,
    "Athlete": 1.9,
}

# ==============================
# 2. CALCULATE CALORIES
# ==============================
if st.button("Calculate My Calories"):
    # BMR
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # TDEE
    tdee = bmr * activity_factor[activity]

    st.success(f"Your Estimated Daily Calorie Intake: **{int(tdee)} kcal**")

    st.subheader("🥗 Recommended Foods for Today")

    # Simple recommendation: choose foods < 300 calories
    recommended = df[df["calories"] <= 300].sample(3)

    st.dataframe(recommended)

    st.write("Note: ini rekomendasi sederhana. Nanti kita ganti dengan model ML.")

