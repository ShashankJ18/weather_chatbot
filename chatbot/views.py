import spacy
import requests
from django.shortcuts import render

# Load the spaCy model
nlp = spacy.load('en_core_web_lg')

# OpenWeatherMap API details
API_KEY = 'dd011755342f91766e0b70e8c9823c58'
BASE_URL = "http://api.openweathermap.org/data/2.5/"

def get_weather_data(location, forecast_type="current"):
    if forecast_type == "current":
        url = f"{BASE_URL}weather?q={location}&appid={API_KEY}&units=metric"
    elif forecast_type == "hourly":
        url = f"{BASE_URL}forecast?q={location}&appid={API_KEY}&units=metric"
    else:
        return "Invalid forecast type"

    print(f"Request URL: {url}")  # Debugging line
    response = requests.get(url)
    
    print(f"Response Status Code: {response.status_code}")  # Debugging line
    print(f"Response Content: {response.text}")  # Debugging line
    
    if response.status_code == 200:
        return response.json()
    else:
        return None


def generate_weather_response(user_input):
    # Default location
    default_location = "London"

    # Extract location from user input if available
    location = default_location
    if "in" in user_input:
        parts = user_input.split("in")
        if len(parts) > 1:
            location = parts[1].strip()

    # Process user input to determine what weather information to fetch
    user_input_lower = user_input.lower()

    # Current weather intent
    if any(word in user_input_lower for word in ["current", "now", "today"]):
        weather_data = get_weather_data(location, "current")
        if weather_data:
            if 'main' in weather_data and 'weather' in weather_data:
                temperature = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                return f"The current weather in {location} is {description} with a temperature of {temperature}°C."
            else:
                return "Received unexpected response from the weather API."
        else:
            return "Sorry, I couldn't fetch the current weather data."
    
    # Forecast for next few hours
    elif any(word in user_input_lower for word in ["hour", "later", "forecast"]):
        weather_data = get_weather_data(location, "hourly")
        if weather_data:
            if 'list' in weather_data:
                forecast = weather_data['list'][0]
                temp = forecast['main']['temp']
                desc = forecast['weather'][0]['description']
                return f"The forecast for the next few hours in {location} is {desc} with a temperature of {temp}°C."
            else:
                return "Received unexpected response from the weather API."
        else:
            return "Sorry, I couldn't fetch the hourly forecast."
    
    # Weather for tomorrow
    elif "tomorrow" in user_input_lower:
        weather_data = get_weather_data(location, "hourly")
        if weather_data:
            if 'list' in weather_data:
                forecast = weather_data['list'][8]  # Roughly 24 hours later
                temp = forecast['main']['temp']
                desc = forecast['weather'][0]['description']
                return f"The weather tomorrow in {location} is expected to be {desc} with a temperature of {temp}°C."
            else:
                return "Received unexpected response from the weather API."
        else:
            return "Sorry, I couldn't fetch the weather for tomorrow."
    
    return "I'm not sure how to help with that. Could you ask something else about the weather?"




# Main chatbot view
def chatbot(request):
    response = ''
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        response = generate_weather_response(user_input)
    return render(request, 'chatbot.html', {'response': response})

