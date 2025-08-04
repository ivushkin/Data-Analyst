import logging
import os
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# загружаем Api бота и ID chat куда бот будет отправлять сообщение
load_dotenv()

# Включаем логи, формат лог-сообщений: включает время, имя логгера, уровень и сообщение. Уровень выше INFO
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Используется range(5) для создания перечисления состояний в виде целых чисел. Это используется в ConversationHandler для определения текущего шага в диалоге с пользователем.
(
    START_STATE,
    SERVICE_STATE,
    DURATION_STATE,
    NAME_STATE,
    PHONE_STATE,
    PROBLEM_STATE,
) = range(6)


# --- Вспомогательная функция для создания клавиатуры ---
# --- Отдаем в функцию Список текстовых меток кнопок и Префикс для callback_data каждой кнопки, чтобы в дальнейшем понимать, на какую кнопку нажал пользователь. Возвращаем клавиатуру в ответном сообщении
def create_keyboard(button_labels, callback_prefix):
    """Создаем inline-клавиатуру с метками кнопок."""
    keyboard = []
    for label in button_labels:
        callback_data = f"{callback_prefix}_{label}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    return InlineKeyboardMarkup(keyboard)


# --- Обработчики команд ---
# --- После нажатия кнопки старт отправляем приветственное сообщение пользовател и предлагаем выбрать тип
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for service type."""
    await update.message.reply_text(
        "Мы можем записать Вас на консультацию к специалистам в нашего Бюро. Пожалуйста, выберите формат ее проведения.",
        reply_markup=create_keyboard(
            ["Очная консультация", "Консультация онлайн"], callback_prefix="service"
        ),
    )
    return SERVICE_STATE


async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем нажатие кнопки выбора услуги."""
    query = update.callback_query
    await query.answer()
    service = query.data.split("_")[1]
    context.user_data["service"] = service

    await query.edit_message_text(
        "Выберите ожидаемую продолжительность встречи",
        reply_markup=create_keyboard(["30 минут", "1 час", "1,5 часа", "2 часа"], callback_prefix="duration"),
    )
    return DURATION_STATE


async def handle_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем продолжительность и спрашиваем имя пользователя."""
    query = update.callback_query
    await query.answer()
    duration = query.data.split("_")[1]
    context.user_data["duration"] = duration
    await query.edit_message_text("Как можно к Вам обращаться?")
    return NAME_STATE


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем имя и спрашиваем номер телефона."""
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text(
        "Введите номер телефона по которому наши специалисты смогут с Вами связаться (в любом формате)")
    return PHONE_STATE


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем телефон и запрашиваем описание проблемы."""
    phone = update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text("Кратко опишите вашу проблему")
    return PROBLEM_STATE


async def handle_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем описание проблемы и отправляем финальное сообщение."""
    problem = update.message.text
    context.user_data["problem"] = problem

    # Получаем данные из переменной
    user_data = context.user_data
    name = user_data.get("name", "Не указано")
    service = user_data.get("service", "Не выбрано")
    duration = user_data.get("duration", "Не выбрано")
    phone = user_data.get("phone", "Не указано")
    problem = user_data.get("problem", "Не указано")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Формируем сообщение для пользователя
    user_message = (
        f"Спасибо, {name}, за ваше обращение!\n"
        f"Мы свяжемся с вами в ближайшее время."
    )

    # Отправляем сообщение пользователю
    await update.message.reply_text(user_message)

    # Отправляем сообщение в чат администратора с данными клиента
    admin_message = (
        f"Внимание! Новый клиент:\n \n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Услуга: {service}\n"
        f"Продолжительность: {duration}\n"
        f"Проблема: {problem}\n"
        f"Время обращения: {timestamp}\n"
    )

    # Отправить сообщение
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        await context.bot.send_message(chat_id=admin_chat_id, text=admin_message)
    else:
        logger.error("ADMIN_CHAT_ID not found in environment variables.")

    # очистить поле
    context.user_data.clear()

    # Конец диалога
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Действие, если пользователь ввел команду /cancel."""
    await update.message.reply_text("Запись отменена, для продолжения нажмите команду /start из меню.")
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Старт бота."""
    # получаем токен бота
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Если токен не найден, регистрирует ошибку и завершает работу.
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    # Создает приложение бота на основе токена.
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SERVICE_STATE: [CallbackQueryHandler(handle_service, pattern="^service_")],
            DURATION_STATE: [CallbackQueryHandler(handle_duration, pattern="^duration_")],
            NAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            PHONE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            PROBLEM_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_problem)],
            # Добавили состояние в ConversationHandler
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
