import telebot
from datetime import datetime, timedelta
import requests
from io import BytesIO
import schedule
import time


# Бот токен должен быть вставлен от своего бота
BOT_TOKEN = 'TOKEN BOT'
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# Вместо 'YOUR_CHAT_ID' надо вставить ID чата
CHAT_ID = '0000000000'

# API-ключ для OpenWeatherMap (замените на свой ключ)
API_KEY = '30e79b1dbc40496744c92e507e54aef2'

cities = {
    'Москва': {'lat': 55.7522, 'lon': 37.6156},
    'Оренбург': {'lat': 51.7727, 'lon': 55.0988},
    'Сочи': {'lat': 43.5992, 'lon': 39.7257}
}

## Формат вызова API https://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid=30e79b1dbc40496744c92e507e54aef2
def get_weather(lat, lon):
    """Получает сводку погоды по координатам."""
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(complete_url)
    response.raise_for_status()  # Обработка ошибок HTTP
    data = response.json()

    if data["cod"] != 200:
        return f"Ошибка получения данных о погоде: {data['message']}"

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    city_name = data["name"]  # Получаем имя города из ответа API
    return f"В городе {city_name}: температура {temp:.1f}°C, {description}"


#Функция автоматической отправки погоды по расписанию
def send_weather_report():
    weather_report = ""
    try:
        for city_name, coords in cities.items():
            weather = get_weather(coords['lat'], coords['lon'])
            weather_report += f" {weather}\n"
        bot.send_message(CHAT_ID, weather_report)  # Отправляем в CHAT_ID
    except Exception as e:
        print(f"Ошибка при отправке отчета о погоде: {e}")


# Настройка расписания
schedule.every().day.at("17:05").do(send_weather_report)

# Бесконечный цикл для выполнения запланированных задач
while True:
    schedule.run_pending()
    time.sleep(5)  # Проверка расписания каждые 5 сек

#bot.infinity_polling(timeout=90, long_polling_timeout = 5)
