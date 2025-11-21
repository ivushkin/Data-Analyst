import telebot
from datetime import datetime, timedelta
import requests
from io import BytesIO
import threading
import schedule
import time

# Бот токен должен быть вставлен от своего бота
BOT_TOKEN = '__________'
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# Вместо 'YOUR_CHAT_ID' надо вставить ID чата
CHAT_ID = '__________'

# URL картинки для будущего события
IMAGE_URL = "https://moskultura.ru/wp-content/uploads/2021/11/muzei_kosmos_obelisk-e1637600066388-1536x995.jpeg"

# URL картинки для прошедшего события
PAST_EVENT_IMAGE_URL = "https://hdpic.club/uploads/posts/2021-12/1639626218_1-hdpic-club-p-samolet-posadka-1.jpg"

# API-ключ для OpenWeatherMap
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
            weather_report += f"{weather}\n\n"
        bot.send_message(CHAT_ID, weather_report)  # Отправляем в CHAT_ID
    except Exception as e:
        print(f"Ошибка при отправке отчета о погоде: {e}")


def schedule_func():
    schedule.every().day.at("09:00").do(send_weather_report)
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
        event_date = datetime(2025, 12, 31, 12, 5)
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


# Функция получения погоды
def get_weather(lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(complete_url)
    response.raise_for_status()
    data = response.json()

    if data["cod"] != 200:
        return f"Ошибка получения данных о погоде: {data['message']}"

    city = data["name"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    wind_gust = data["wind"].get("gust", "нет данных")
    clouds = data["clouds"]["all"]
    description = data["weather"][0]["description"]

    weather_report = (
        f"📍 Город: {city}\n"
        f"🌡 Температура: {temp:.1f}°C, ощущается как {feels_like:.1f}°C \n"
        f"💧 Влажность: {humidity}%\n"
        f"💨 Ветер: Скорость: {wind_speed} м/с с порывами: {wind_gust} м/с \n "
        f"☁ Облачность: {clouds}%\n"
        f"🌈 Погода: {description}"
    )

    return weather_report


@bot.message_handler(commands=['weather'])
def send_weather(message):
    weather_report = ""
    for city_name, coords in cities.items():
        weather = get_weather(coords['lat'], coords['lon'])
        weather_report += f"{weather}\n\n"  #
    bot.reply_to(message, weather_report)


@bot.message_handler(commands=['vnechata'])
def send_available_days(message):
    """Отправляет список доступных на этой неделе дней для мероприятий"""
    try:
        # Фиксированная точка отсчета
        base_date = datetime(2025, 11, 21).date()  # 21.11.2025 - день
        today = datetime.now().date()

        # Определяем дни недели для текущей недели (с понедельника по воскресенье)
        start_of_week = today - timedelta(days=today.weekday())  # Понедельник этой недели
        end_of_week = start_of_week + timedelta(days=6)  # Воскресенье этой недели

        available_days = []
        current_day = start_of_week

        # Перебираем все дни недели
        while current_day <= end_of_week:
            # Вычисляем разницу в днях от базовой даты (21.11.2025)
            days_from_base = (current_day - base_date).days

            if days_from_base >= 0:
                # Применяем логику: 21.11 - день, 22.11 - ночь, 23-24.11 - отдых, 25.11 - день и т.д.
                cycle_position = days_from_base % 4

                # В цикле 4 позиции: 0-день, 1-ночь, 2-отдых, 3-отдых
                # Доступны только дни отдыха (позиции 2 и 3)
                if cycle_position == 2 or cycle_position == 3:
                    available_days.append(current_day)

            current_day += timedelta(days=1)

        # Форматируем дни в русские названия
        days_names = {
            0: "понедельник",
            1: "вторник",
            2: "среду",
            3: "четверг",
            4: "пятницу",
            5: "субботу",
            6: "воскресенье"
        }

        # Преобразуем даты в названия дней недели
        available_day_names = [days_names[day.weekday()] for day in available_days]

        # Формируем фразу ответа
        if available_day_names:
            if len(available_day_names) == 1:
                days_text = available_day_names[0]
            elif len(available_day_names) == 2:
                days_text = " и ".join(available_day_names)
            else:
                days_text = ", ".join(available_day_names[:-1]) + " и " + available_day_names[-1]

            response_text = f"На этой неделе с Сашей @Aleksandrg31 возможно провести сбор в {days_text}."
        else:
            response_text = "На этой неделе нет доступных дней для сборов."

        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Ошибка при определении доступных дней: {e}")
        bot.reply_to(message, "Произошла ошибка при определении доступных дней. Попробуйте позже.")


bot.infinity_polling(timeout=90, long_polling_timeout=5)
