from datetime import datetime
import requests
import time
import json
import sqlite3

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

API_KEY = config["api_key"]  # Your OpenWeatherMap API key
CITIES = config["cities"]  # List of cities to monitor
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# Database setup
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS daily_summaries
                  (date TEXT, avg_temp REAL, max_temp REAL, min_temp REAL, condition TEXT)''')

def get_weather_data(city):
    complete_url = f"{BASE_URL}q={city}&appid={API_KEY}"
    response = requests.get(complete_url)
    return response.json()

def process_weather_data(data):
    temp = data['main']['temp'] - 273.15  # Convert to Celsius
    condition = data['weather'][0]['main']
    dt = datetime.fromtimestamp(data['dt']).date()
    return {
        "temp": temp,
        "condition": condition,
        "date": str(dt)
    }

def monitor_weather():
    daily_summaries = {}
    alert_threshold = 35  # Example threshold
    try:
        while True:
            for city in CITIES:
                data = get_weather_data(city)
                processed_data = process_weather_data(data)

                date = processed_data['date']
                if date not in daily_summaries:
                    daily_summaries[date] = {
                        "temp_sum": 0, 
                        "count": 0, 
                        "max_temp": float('-inf'), 
                        "min_temp": float('inf'), 
                        "conditions": []
                    }

                daily_summaries[date]['temp_sum'] += processed_data['temp']
                daily_summaries[date]['count'] += 1
                daily_summaries[date]['max_temp'] = max(daily_summaries[date]['max_temp'], processed_data['temp'])
                daily_summaries[date]['min_temp'] = min(daily_summaries[date]['min_temp'], processed_data['temp'])
                daily_summaries[date]['conditions'].append(processed_data['condition'])

                # Check for alerts
                if processed_data['temp'] > alert_threshold:
                    print(f"Alert! {city} has exceeded the threshold with a temperature of {processed_data['temp']:.2f}°C.")

                # Display temperature for each city
                print(f"City: {city}, Temp: {processed_data['temp']:.2f}°C, Condition: {processed_data['condition']}")

            # Store daily summaries
            for date, summary in daily_summaries.items():
                avg_temp = summary['temp_sum'] / summary['count']
                dominant_condition = max(set(summary['conditions']), key=summary['conditions'].count)
                cursor.execute("INSERT INTO daily_summaries (date, avg_temp, max_temp, min_temp, condition) VALUES (?, ?, ?, ?, ?)",
                               (date, avg_temp, summary['max_temp'], summary['min_temp'], dominant_condition))
                conn.commit()

                print(f"Date: {date}, Avg Temp: {avg_temp:.2f}°C, Max Temp: {summary['max_temp']:.2f}°C, Min Temp: {summary['min_temp']:.2f}°C, Dominant Condition: {dominant_condition}")

            print("Waiting for the next update...")
            time.sleep(300)  # Wait for 5 minutes
    except KeyboardInterrupt:
        print("Weather monitoring stopped by user.")
    finally:
        conn.close()

if __name__ == "__main__":
    monitor_weather()
