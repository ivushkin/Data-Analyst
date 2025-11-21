import requests
import json


def test_weather_api():
    """Тестовый скрипт для анализа полного JSON от погодного API"""

    API_KEY = '30e79b1dbc40496744c92e507e54aef2'

    # Тестовые координаты Москвы
    lat = 55.7522
    lon = 37.6156

    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        print("=" * 50)
        print("ПОЛНЫЙ JSON ОТ ПОГОДНОГО API:")
        print("=" * 50)
        print(json.dumps(data, indent=2, ensure_ascii=False))

        print("\n" + "=" * 50)
        print("АНАЛИЗ ДОСТУПНЫХ ДАННЫХ:")
        print("=" * 50)

        # Основная информация
        if "name" in data:
            print(f"📍 Город: {data['name']}")

        # Координаты
        if "coord" in data:
            print(f"🎯 Координаты: {data['coord']}")

        # Основные погодные данные
        if "main" in data:
            main = data["main"]
            print(f"🌡 Температура: {main.get('temp')}°C")
            print(f"🤒 Ощущается как: {main.get('feels_like')}°C")
            print(f"📊 Давление: {main.get('pressure')} hPa")
            print(f"💧 Влажность: {main.get('humidity')}%")
            print(f"📈 Мин. температура: {main.get('temp_min')}°C")
            print(f"📉 Макс. температура: {main.get('temp_max')}°C")

        # Видимость
        if "visibility" in data:
            print(f"👁 Видимость: {data['visibility']} метров")

        # Ветер
        if "wind" in data:
            wind = data["wind"]
            print(f"💨 Ветер: {wind}")
            if "speed" in wind:
                print(f"  📏 Скорость: {wind['speed']} м/с")
            if "deg" in wind:
                print(f"  🧭 Направление: {wind['deg']}°")
            if "gust" in wind:
                print(f"  💨 Порывы: {wind['gust']} м/с")

        # Облачность
        if "clouds" in data:
            print(f"☁ Облачность: {data['clouds'].get('all')}%")

        # Погодные условия
        if "weather" in data and len(data["weather"]) > 0:
            weather = data["weather"][0]
            print(f"🌈 Погода: {weather}")
            print(f"  📝 Описание: {weather.get('description')}")
            print(f"  🎨 Основное: {weather.get('main')}")
            print(f"  🆔 ID: {weather.get('id')}")
            print(f"  🖼 Иконка: {weather.get('icon')}")

        # Восход и закат
        if "sys" in data:
            sys = data["sys"]
            if "sunrise" in sys:
                from datetime import datetime
                sunrise = datetime.fromtimestamp(sys['sunrise']).strftime('%H:%M')
                print(f"🌅 Восход: {sunrise}")
            if "sunset" in sys:
                sunset = datetime.fromtimestamp(sys['sunset']).strftime('%H:%M')
                print(f"🌇 Закат: {sunset}")
            if "country" in sys:
                print(f"🇷🇺 Страна: {sys['country']}")

        # Дополнительная информация
        if "timezone" in data:
            print(f"⏰ Часовой пояс: {data['timezone']} секунд")

        if "dt" in data:
            from datetime import datetime
            dt = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"🕐 Время данных: {dt}")

        print("\n" + "=" * 50)
        print("ПРЕДЛАГАЕМЫЙ ФОРМАТ ОТВЕТА:")
        print("=" * 50)

        # Пример расширенного формата
        if all(key in data for key in ['name', 'main', 'weather', 'wind']):
            city = data['name']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']

            extended_weather = (
                f"📍 {city}:\n"
                f"🌡 {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
                f"🌈 {description.capitalize()}\n"
                f"💧 Влажность: {humidity}%\n"
                f"📊 Давление: {pressure} hPa\n"
                f"💨 Ветер: {wind_speed} м/с"
            )

            print(extended_weather)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    except KeyError as e:
        print(f"Ошибка в структуре JSON: отсутствует ключ {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


# Запускаем тест
if __name__ == "__main__":
    test_weather_api()