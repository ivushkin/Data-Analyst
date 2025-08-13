import telebot
from datetime import datetime, timedelta
import requests
from io import BytesIO
import threading
import schedule
import time

# Бот токен должен быть вставлен от своего бота
BOT_TOKEN = 'YOU_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# Вместо 'YOUR_CHAT_ID' надо вставить ID чата
CHAT_ID = 'YOUR_CHAT_ID'

# URL картинки для будущего события
IMAGE_URL = "https://example.jpg"

# URL картинки для прошедшего события
PAST_EVENT_IMAGE_URL = "https://example.jpg"

# API-ключ для OpenWeatherMap (замените на свой ключ)
API_KEY = '30e79b1dbc40496744c92e507e54aef2'

cities = {
    'Москва': {'lat': 55.7522, 'lon': 37.6156},
    'Оренбург': {'lat': 51.7727, 'lon': 55.0988},
    'Сочи': {'lat': 43.5992, 'lon': 39.7257}
}

# Функция автоматической отправки погоды по расписанию
def send_weather_report():
    weather_report = ""
    try:
        for city_name, coords in cities.items():
            weather = get_weather(coords['lat'], coords['lon'])
            weather_report += f" {weather}\n"
        bot.send_message(CHAT_ID, weather_report)  # Отправляем в CHAT_ID
    except Exception as e:
        print(f"Ошибка при отправке отчета о погоде: {e}")

def schedule_func():
    schedule.every().day.at("06:00").do(send_weather_report)
    while True:
        schedule.run_pending()
        time.sleep(30)

# Запуск потока для расписания
weather_thread = threading.Thread(target=schedule_func)
weather_thread.daemon = True
weather_thread.start()

@bot.message_handler(commands=['time_to_image'])
def send_time_to_event_with_image(message):
    """Отправляет сообщение с картинкой об остатке времени до события."""
    try:
        event_date = datetime(2025, 8, 23, 12, 5)
        time_left = event_date - datetime.now()

        if time_left > timedelta(0):
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            message_text = f"До приезда братана осталось: {days} дней, {hours} часов, {minutes} минут, {seconds} секунд."

            # Загружаем картинку для будущего события
            response = requests.get(IMAGE_URL, stream=True)
            response.raise_for_status()
            image = BytesIO(response.content)
            bot.send_photo(message.chat.id, image, caption=message_text)

        elif time_left == timedelta(0):
            bot.send_message(message.chat.id, "Событие сейчас!")

        else:
            message_text = "Братан уже приехал, дата следующего приезда не определена."

            # Загружаем картинку для прошедшего события
            response = requests.get(PAST_EVENT_IMAGE_URL, stream=True)
            response.raise_for_status()
            image = BytesIO(response.content)
            bot.send_photo(message.chat.id, image, caption=message_text)

    except (IndexError, ValueError, requests.exceptions.RequestException, OverflowError):
        bot.reply_to(message, "Ошибка! Неверный формат даты или проблемы с загрузкой картинки. Попробуйте еще раз.")

# Получение погоды
def get_weather(lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(complete_url)
    response.raise_for_status()
    data = response.json()

    if data["cod"] != 200:
        return f"Ошибка получения данных о погоде: {data['message']}"

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    city_name = data["name"]
    return f"В городе {city_name}: температура {temp:.1f}°C, {description}"

@bot.message_handler(commands=['weather'])
def send_weather(message):
    weather_report = ""
    for city_name, coords in cities.items():
        weather = get_weather(coords['lat'], coords['lon'])
        weather_report += f"{weather}\n"
    bot.reply_to(message, weather_report)

bot.infinity_polling(timeout=90, long_polling_timeout=5)
