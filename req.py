import requests
import urllib.parse

def get_weather(city,state, country):
    API_KEY = "4ee63cd8e491cb1d839e3ad46a5f6e0"
    # Get coordinates
    coordinate_url = f"https://api.openweathermap.org/geo/1.0/direct?q={urllib.parse.quote(city)},{state},{country}&limit=1&appid={API_KEY}"
    # print("#########coordinate_url########"+coordinate_url)
    coordinate_response = requests.get(coordinate_url)
    data = coordinate_response.json()
    # print(data)
    latitude = round(data[0]['lat'], 2)
    longitude = round(data[0]['lon'], 2)  
    # Get weather data
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY
    }
    response = requests.get(url, params=params)
    # print(response.json())  
    # Check response status
    if response.status_code == 200:
        # print("############"+city)
        # print("############"+data)
        return parse_weather_data(response.json())
    else:
        # print("############"+city)
        # print("############"+data)
        return f"Error: {response.status_code}"

def parse_weather_data(data):
    # Parsing required fields
    description = data['weather'][0]['description']
    main_weather = data['weather'][0]['main']
    wind_speed_mps = data['wind']['speed']
    wind_speed_mph = wind_speed_mps * 2.237    
    # Convert temperatures from Kelvin to Fahrenheit
    temp_kelvin = data['main']['temp']
    temp_fahrenheit = round((temp_kelvin - 273.15) * 9/5 + 32 ,0)
    
    # Creating JSON object
    parsed_data = {
        'description': description,
        'main': main_weather,
        'temps': {
            'temp': temp_fahrenheit,
            'feels_like': round(((data['main']['feels_like'] - 273.15) * 9/5) + 32,0),
            'temp_min': round(((data['main']['temp_min'] - 273.15) * 9/5) + 32,0),
            'temp_max': round(((data['main']['temp_max'] - 273.15) * 9/5) + 32,0)
        },
        'wind': {
            'speed': round(wind_speed_mph, 2),
            'deg': data['wind']['deg']
        }
    }
    return parsed_data

# if __name__ == '__main__':
#     print(get_weather('CT', 'US'))
