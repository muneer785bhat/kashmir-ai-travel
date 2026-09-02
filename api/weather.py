import os
import requests


WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"


CITIES = {
    "srinagar": {
        "name": "Srinagar",
        "lat": 34.0837,
        "lon": 74.7973
    },

    "gulmarg": {
        "name": "Gulmarg",
        "lat": 34.0484,
        "lon": 74.3805
    },

    "pahalgam": {
        "name": "Pahalgam",
        "lat": 34.0161,
        "lon": 75.3150
    },

    "sonamarg": {
        "name": "Sonamarg",
        "lat": 34.3029,
        "lon": 75.2931
    },

    "doodhpathri": {
        "name": "Doodhpathri",
        "lat": 33.8395,
        "lon": 74.6590
    },

    "gurez": {
        "name": "Gurez Valley",
        "lat": 34.6333,
        "lon": 74.8333
    }
}


def get_weather(city):

    if not WEATHER_API_KEY:
        raise ValueError(
            "OPENWEATHER_API_KEY is not configured."
        )


    city = city.lower().strip()


    if city not in CITIES:
        raise ValueError(
            "Unknown Kashmir destination."
        )


    location = CITIES[city]


    current_response = requests.get(

        f"{BASE_URL}/weather",

        params={
            "lat": location["lat"],
            "lon": location["lon"],
            "appid": WEATHER_API_KEY,
            "units": "metric"
        },

        timeout=15
    )
    print("Weather API status:", current_response.status_code)
    print("Weather API response:", current_response.text)

    current_response.raise_for_status()


    current = current_response.json()


    forecast_response = requests.get(

        f"{BASE_URL}/forecast",

        params={
            "lat": location["lat"],
            "lon": location["lon"],
            "appid": WEATHER_API_KEY,
            "units": "metric"
        },

        timeout=15
    )


    forecast_response.raise_for_status()


    forecast = forecast_response.json()


    return {

        "city": location["name"],

        "temperature": round(
            current["main"]["temp"]
        ),

        "feels_like": round(
            current["main"]["feels_like"]
        ),

        "humidity": current["main"]["humidity"],

        "wind_speed": round(
            current["wind"]["speed"] * 3.6,
            1
        ),

        "condition":
            current["weather"][0]["main"],

        "description":
            current["weather"][0]["description"],

        "icon":
            current["weather"][0]["icon"],

        "forecast": [

            {
                "date":
                    item["dt_txt"],

                "temperature":
                    round(
                        item["main"]["temp"]
                    ),

                "condition":
                    item["weather"][0]["main"],

                "description":
                    item["weather"][0]["description"],

                "icon":
                    item["weather"][0]["icon"]
            }

            for item in forecast["list"][:8]

        ]

    }