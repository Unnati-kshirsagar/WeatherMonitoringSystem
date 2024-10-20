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
    try:
        while True:
            # Create a dictionary to store city-wise summaries
            city_summaries = {}
            for city in CITIES:
                data = get_weather_data(city)
                if 'main' in data and 'weather' in data:
                    processed_data = process_weather_data(data)

                    # Store data for the city
                    city_summaries[city] = {
                        "temp": processed_data['temp'],
                        "condition": processed_data['condition'],
                        "date": processed_data['date']
                    }
                else:
                    print(f"Error retrieving data for {city}: {data.get('message', 'Unknown error')}")

            # Calculate average, max, and min temperatures
            avg_temp = sum(summary["temp"] for summary in city_summaries.values()) / len(city_summaries)
            max_temp = max(summary["temp"] for summary in city_summaries.values())
            min_temp = min(summary["temp"] for summary in city_summaries.values())

            # Print weather data for each city
            for city, summary in city_summaries.items():
                print(f"City: {city}, Temp: {summary['temp']:.2f}°C, Condition: {summary['condition']}, Date: {summary['date']}")

            # Print overall summary
            print(f"Average Temp: {avg_temp:.2f}°C, Max Temp: {max_temp:.2f}°C, Min Temp: {min_temp:.2f}°C")
            print("Waiting for the next update...")
            time.sleep(300)  # Wait for 5 minutes before fetching the data again
    except KeyboardInterrupt:
        print("Weather monitoring stopped by user.")

if __name__ == "__main__":
    monitor_weather()
