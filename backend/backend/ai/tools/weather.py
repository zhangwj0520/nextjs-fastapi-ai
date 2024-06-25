import os
from typing import Optional

import requests
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


class WeatherInput(BaseModel):
    city: str = Field(..., description="要查询天气的城市")
    # state: str = Field(
    #     ..., description="The two letter state abbreviation to get weather for"
    # )
    # country: Optional[str] = Field(
    #     "usa", description="The two letter country abbreviation to get weather for"
    # )


@tool("weather-data", args_schema=WeatherInput, return_direct=True)
def weather_data(city: str) -> dict:
    """获取当前城市的天气情况."""
    amap_key = os.environ.get("AMAP_KEY")
    if not amap_key:
        raise ValueError("Missing amap_key secret.")

    # # geocode_url = f"https://geocode.xyz/{city.lower()},{state.lower()},{country.lower()}?json=1&auth={geocode_api_key}"
    amap_city_url = f"https://restapi.amap.com/v3/config/district?key={amap_key}&keywords={city}&&subdistrict=0&extensions=base"

    city_response = requests.get(amap_city_url)
    if not city_response.ok:
        print("城市位置查询错误")
        raise ValueError("城市位置查询错误")
    city_data = city_response.json()
    print("city_response", city_data)

    adcode = city_data["districts"][0]["adcode"]
    print("adcode", adcode)

    #  查询天气
    amap_weather_url = (
        f"https://restapi.amap.com/v3/weather/weatherInfo?key={amap_key}&city={adcode}"
    )

    weather_response = requests.get(amap_weather_url)
    if not weather_response.ok:
        print("天气查询失败")
        raise ValueError("天气查询失败")
    weather_data = weather_response.json()
    print("weather_data", weather_data)

    return {
        "province": weather_data["lives"][0]["province"],
        "city": weather_data["lives"][0]["city"],
        "weather": weather_data["lives"][0]["weather"],
        "temperature": weather_data["lives"][0]["temperature"],
        "reporttime": weather_data["lives"][0]["reporttime"],
    }
