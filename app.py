import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# Title
st.title("Weather Dashboard")
st.caption("Live weather insights for any city")

# Sidebar input
st.sidebar.header("Search")
city = st.sidebar.text_input("Enter a city", "Johannesburg")

# Function: Get coordinates
@st.cache_data
def get_coordinates(city_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
    response = requests.get(geo_url)
    data = response.json()

    if "results" in data:
        result = data["results"][0]
        return result["latitude"], result["longitude"], result["name"]
    return None, None, None

# Function: Fetch weather
@st.cache_data
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=temperature_2m,windspeed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min"
    )
    response = requests.get(url)
    return response.json()

# Get coordinates
lat, lon, location_name = get_coordinates(city)

if lat and lon:

    st.success(f"Location: {location_name}")

    # Loading spinner
    with st.spinner("Fetching weather data..."):
        data = fetch_weather(lat, lon)

    weather = data.get("current_weather")

    if weather:
        temperature = weather["temperature"]
        windspeed = weather["windspeed"]
        winddirection = weather["winddirection"]

        # Simulated humidity
        humidity = round(60 + (temperature % 10))

        # Layout
        left_col, right_col = st.columns([1, 2])

        # Left panel (current weather)
        with left_col:
            st.subheader("Current Weather")

            st.metric("Temperature (°C)", temperature)
            st.metric("Humidity (%)", humidity)
            st.metric("Wind Speed (km/h)", windspeed)
            st.metric("Wind Direction", winddirection)

        # Right panel (charts)
        with right_col:
            hourly = data.get("hourly")

            if hourly:
                df_hourly = pd.DataFrame({
                    "time": hourly["time"],
                    "temperature": hourly["temperature_2m"],
                    "wind": hourly["windspeed_10m"]
                })

                st.subheader("Temperature Trend (24h)")
                st.line_chart(df_hourly.set_index("time")[["temperature"]])

                st.subheader("Wind Speed Trend")
                st.line_chart(df_hourly.set_index("time")[["wind"]])

    st.markdown("---")

    # 7-day forecast
    st.subheader("7-Day Forecast")

    daily = data.get("daily")

    if daily:
        df_daily = pd.DataFrame({
            "date": daily["time"],
            "max_temp": daily["temperature_2m_max"],
            "min_temp": daily["temperature_2m_min"]
        })

        st.dataframe(df_daily)

        st.subheader("Weekly Temperature Range")
        st.line_chart(df_daily.set_index("date"))

else:
    st.error("City not found. Please enter a valid location.")