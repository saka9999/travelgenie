import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from itertools import product

st.set_page_config("✈️ TravelGenie", layout="wide")
st.title("✈️ TravelGenie – AI Flight Booker (LIVE Search)")

# Sidebar inputs
with st.sidebar:
    st.header("✈️ Travel Preferences")
    origin = st.text_input("From (IATA code)", "BOM")
    destination = st.text_input("To (IATA code)", "SEA")
    journey_type = st.selectbox("Journey Type", ["Return", "One-way"])
    passengers = st.slider("Passengers", 1, 5, 1)
    travel_class = st.selectbox("Class", ["Economy", "Business"])
    currency = st.selectbox("Currency", ["INR", "USD"])
    max_stops = st.selectbox("Max Stops", [0, 1])
    max_duration = st.slider("Max Duration per leg (hrs)", 8, 40, 26)

# Date inputs
st.subheader("📅 Select Date Ranges")
col1, col2 = st.columns(2)
with col1:
    depart_start = st.date_input("Departure Start", datetime(2025, 6, 20))
    depart_end = st.date_input("Departure End", datetime(2025, 6, 30))
with col2:
    return_start = st.date_input("Return Start", datetime(2025, 12, 1))
    return_end = st.date_input("Return End", datetime(2025, 12, 10))

# Weekday combinations
weekday_options = ["Mon-Tue", "Tue-Wed", "Wed-Thu", "Thu-Fri", "Fri-Sat", "Sat-Sun", "Sun-Mon"]
selected_combos = st.multiselect("Preferred Weekday Combinations", weekday_options, default=weekday_options)

# Function to generate weekday date pairs
def generate_date_pairs(start1, end1, start2, end2, combo):
    day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    dep_day, ret_day = combo.split("-")
    dep_dates = [start1 + timedelta(days=i) for i in range((end1 - start1).days + 1) if (start1 + timedelta(days=i)).weekday() == day_map[dep_day]]
    ret_dates = [start2 + timedelta(days=i) for i in range((end2 - start2).days + 1) if (start2 + timedelta(days=i)).weekday() == day_map[ret_day]]
    return list(product(dep_dates, ret_dates))

# Create all date combinations
all_date_combos = []
for combo in selected_combos:
    all_date_combos.extend(generate_date_pairs(depart_start, depart_end, return_start, return_end, combo))

# RUN button
run = st.button("🔍 Run Flight Search")

if run and all_date_combos:
    st.info("Fetching real-time results... please wait ⏳")

    # Prepare payload
    payload = {
        "origin": origin,
        "destination": destination,
        "journey_type": journey_type,
        "passengers": passengers,
        "cabin_class": travel_class,
        "currency": currency,
        "date_combinations": [
            {
                "departure": dep.strftime("%Y-%m-%d"),
                "return_date": ret.strftime("%Y-%m-%d") if journey_type == "Return" else None
            }
            for dep, ret in all_date_combos
        ],
        "max_stops": max_stops,
        "max_duration": max_duration
    }

    # Replace this with your deployed API endpoint
    API_URL = "https://travelgenie-backend.onrender.com/search_flights"

    try:
        res = requests.post(API_URL, json=payload, timeout=180)
        if res.status_code == 200:
            data = res.json()
            if not data:
                st.warning("No flights found for the selected combinations.")
            else:
                df = pd.DataFrame(data)
                df.rename(columns={
                    "departure_date": "Departure Date",
                    "return_date": "Return Date",
                    "airline": "Airline",
                    "price": f"Price ({currency})",
                    "duration_outbound": "Outbound Duration",
                    "duration_return": "Return Duration",
                    "stops_outbound": "Outbound Stops",
                    "stops_return": "Return Stops",
                    "fare_rules": "Fare Rules"
                }, inplace=True)
                st.success(f"Showing best flight options for {len(df)} combinations:")
                st.dataframe(df, use_container_width=True)
        else:
            st.error(f"API Error: {res.status_code} – {res.text}")
    except Exception as e:
        st.exception(f"Failed to connect to API: {e}")

elif run:
    st.warning("No valid date combinations selected.")
