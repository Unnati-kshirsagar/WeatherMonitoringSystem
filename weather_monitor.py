from datetime import datetime
import requests
import time

API_KEY = "03a6053cd33635e18289f62432c1f06a"  # Your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]

def get_weather_data(city):
    complete_url = f"{BASE_URL}q={city}&appid={API_KEY}"
    response = requests.get(complete_url)
    return response.json()

def process_weather_data(data):
    temp = data['main']['temp'] - 273.15  # Convert to Celsius
    feels_like = data['main']['feels_like'] - 273.15
    condition = data['weather'][0]['main']
    dt = datetime.fromtimestamp(data['dt']).date()
    return {
        "temp": temp,
        "feels_like": feels_like,
        "condition": condition,
        "date": dt
    }

def monitor_weather():
    daily_summaries = {}
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

            for date, summary in daily_summaries.items():
                avg_temp = summary['temp_sum'] / summary['count']
                dominant_condition = max(set(summary['conditions']), key=summary['conditions'].count)
                print(f"Date: {date}, Avg Temp: {avg_temp:.2f}°C, Max Temp: {summary['max_temp']:.2f}°C, Min Temp: {summary['min_temp']:.2f}°C, Dominant Condition: {dominant_condition}")

            print("Waiting for the next update...")
            time.sleep(300)  # Wait for 5 minutes before fetching the data again
    except KeyboardInterrupt:
        print("Weather monitoring stopped by user.")

if __name__ == "__main__":
    monitor_weather()
