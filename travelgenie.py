import streamlit as st
import pandas as pd
from itertools import product
from datetime import datetime, timedelta

# --- TravelGenie Interface ---
st.set_page_config("✈️ TravelGenie", layout="wide")
st.title("✈️ TravelGenie AI Flight Booker")

# Inputs
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("🌐 Origin Airport (e.g., DEL)", "DEL")
    destination = st.text_input("🌎 Destination Airport (e.g., JFK)", "JFK")
    journey_type = st.selectbox("🔄 Journey Type", ["Return", "One-way"])
    passengers = st.number_input("👥 Passengers", 1, 10, 1)

with col2:
    travel_class = st.selectbox("💺 Travel Class", ["Economy", "Business"])
    currency = st.selectbox("💱 Currency", ["INR", "USD"])
    max_stops = st.selectbox("🛑 Max Stops Allowed", [0, 1, 2], index=1)
    max_duration = st.slider("⏱️ Max Duration (hrs)", 1, 50, 26)

# Dates selection
col3, col4 = st.columns(2)
with col3:
    depart_range = st.date_input("🗓️ Departure Date Range",
                                 (datetime(2025, 6, 20), datetime(2025, 6, 30)))

with col4:
    return_range = st.date_input("🗓️ Return Date Range",
                                 (datetime(2025, 12, 1), datetime(2025, 12, 10)))

# Weekday combinations
st.subheader("📅 Weekday Combinations")
weekdays = ["Mon-Tue", "Tue-Wed", "Wed-Thu", "Thu-Fri", "Fri-Sat", "Sat-Sun", "Sun-Mon"]
selected_combinations = st.multiselect("Select combinations to try:", weekdays, weekdays)

# Generate dummy combinations (for MVP)
def daterange(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

def weekday_combo(day_str):
    days_map = {
        "Mon": 0, "Tue": 1, "Wed": 2,
        "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
    }
    dep_day, ret_day = day_str.split('-')
    dep_dates = [d for d in daterange(depart_range[0], depart_range[1]) if d.weekday() == days_map[dep_day]]
    ret_dates = [d for d in daterange(return_range[0], return_range[1]) if d.weekday() == days_map[ret_day]]
    return list(product(dep_dates, ret_dates))

# Generate combinations
all_combos = []
for combo in selected_combinations:
    all_combos.extend(weekday_combo(combo))

# Mock results
results = pd.DataFrame({
    "Departure": [c[0] for c in all_combos],
    "Return": [c[1] for c in all_combos],
    "Airline": ["Example Airline"] * len(all_combos),
    "Stops": [max_stops] * len(all_combos),
    "Duration (hrs)": [max_duration - 1] * len(all_combos),
    "Price": [1000] * len(all_combos),
    "Currency": [currency] * len(all_combos)
})

# Display results
st.subheader("🔍 Mock Results (MVP)")
st.dataframe(results, use_container_width=True)
