import os
import requests
from dotenv import load_dotenv
from pprint import pprint
from dataclasses import dataclass
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@dataclass
class WeatherData:
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    wind_speed: float
    wind_deg: str
    icon_url: str

class WeatherInfo:
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def degree_to_direction(degree):
        directions = ['北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東', '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西']
        index = round(degree / 22.5) % 16
        return directions[index]

    def get_current_weather(self, zip_code: str | int):
        url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code},JP&units=metric&appid={self.api_key}"
        response = requests.get(url)
        data = response.json()

        return WeatherData(
            temp=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            temp_min=data["main"]["temp_min"],
            temp_max=data["main"]["temp_max"],
            pressure=data["main"]["pressure"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            wind_deg=self.degree_to_direction(data["wind"]["deg"]),
            icon_url=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
        )

    def get_weather_forecast(self, zip_code: str | int):
        url = f"https://api.openweathermap.org/data/2.5/forecast?zip={zip_code},JP&units=metric&appid={self.api_key}"
        response = requests.get(url)
        return response.json()
