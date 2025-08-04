import telebot
import requests

# Замените 'YOUR_BOT_TOKEN' на свой токен бота
BOT_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

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


@bot.message_handler(commands=['weather'])
def send_weather(message):
    """Отправляет сводку погоды для трех городов."""
    weather_report = ""
    for city_name, coords in cities.items():
        weather = get_weather(coords['lat'], coords['lon'])
        weather_report += f"{weather}\n"
    bot.reply_to(message, weather_report)


bot.infinity_polling(timeout=90, long_polling_timeout = 5)