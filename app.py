from flask import Flask, render_template
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

API_KEY = '6188f0ff8b21c19222a9af0205df2bd4'
CITY_IDS = {
    'Delhi': 1273294,
    'Mumbai': 1275339,
    'Chennai': 1264527,
    'Bangalore': 1277333,
    'Kolkata': 1275004,
    'Hyderabad': 1269843
}
ALERT_THRESHOLD = 35

def get_weather(city_id):
    """Fetch weather data for a city by ID, with error handling."""
    url = f'http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}'
    response = requests.get(url).json()

    if 'name' not in response or 'main' not in response or 'weather' not in response:
        return None  # Return None if the expected keys are missing

    return {
        'city': response.get('name', 'Unknown'),
        'temp': response['main'].get('temp', 0) - 273.15,  # Convert from Kelvin to Celsius
        'feels_like': response['main'].get('feels_like', 0) - 273.15,
        'condition': response['weather'][0].get('main', 'Unknown'),
        'dt': datetime.fromtimestamp(response.get('dt', datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M:%S')
    }

def aggregate_daily_weather(data):
    """Aggregate daily weather data for summary."""
    df = pd.DataFrame(data)
    return {
        'avg_temp': df['temp'].mean(),
        'max_temp': df['temp'].max(),
        'min_temp': df['temp'].min(),
        'dominant_condition': df['condition'].mode()[0] if not df['condition'].empty else 'Unknown'
    }

@app.route('/')
def index():
    """Main route that displays weather data and daily summary."""
    all_weather_data = []
    for city, city_id in CITY_IDS.items():
        weather = get_weather(city_id)
        if weather:
            all_weather_data.append(weather)

    daily_summary = aggregate_daily_weather(all_weather_data) if all_weather_data else None

    return render_template('index.html', weather_data=all_weather_data, daily_summary=daily_summary)

if __name__ == '__main__':
    app.run(debug=True ,port=8000)
