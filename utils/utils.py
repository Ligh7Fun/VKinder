import os
import requests

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# api.geonames.org key
geonames_key = os.getenv("GEONAMES_KEY")


def calculate_age(birth_date: str) -> int:
    """
    Рассчитывает возраст на основе заданной даты рождения.

    Args:
        birth_date (str): Дата рождения в формате 'дд.мм.гггг'.

    Returns:
        int: Рассчитанный возраст на основе текущей даты.

    """
    birth_date = datetime.strptime(birth_date, '%d.%m.%Y')
    current_date = datetime.now()
    age = current_date.year - birth_date.year
    if current_date.month < birth_date.month or \
            (current_date.month == birth_date.month
             and current_date.day < birth_date.day):
        age -= 1

    return age


def get_country_iso(city_name: str) -> str | None:
    """
    Получает код страны в формате ISO 3166-1 alpha-2 по названию города.

    Args:
        city_name (str): Название города.

    Returns:
        str | None: Код страны в формате ISO 3166-1 alpha-2,
            если город найден, иначе None.
    """
    url = (f"http://api.geonames.org/searchJSON?q="
           f"{city_name}&maxRows=1&username={geonames_key}")
    response = requests.get(url)
    data = response.json()
    if "geonames" in data and len(data["geonames"]) > 0:
        country_code = data["geonames"][0]["countryCode"]
        return country_code
    return None
