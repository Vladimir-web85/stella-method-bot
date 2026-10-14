import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from app.numerology import life_path_number, interpretation
from app.tarot import draw_reflection_card
from app.report import build_report
from app.astrology import astrology_status

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔢 Нумерология", callback_data="numerology")],
    [InlineKeyboardButton("🌌 Астрология", callback_data="astrology")],
    [InlineKeyboardButton("🃏 Таро и архетипы", callback_data="tarot")],
    [InlineKeyboardButton("✨ Комплексный разбор", callback_data="report")],
    [InlineKeyboardButton("ℹ️ О проекте", callback_data="about")],
])

WELCOME = (
    "✨ Добро пожаловать в Stella\n\n"
    "Твой помощник для символического самопознания.\n"
    "Здесь можно исследовать числа, архетипы и вопросы для размышления.\n\n"
    "Выбери раздел в меню. Это не инструмент достоверного предсказания будущего."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_birthdate", None)
    await update.effective_message.reply_text(WELCOME, reply_markup=MENU)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Как пользоваться Stella:\n"
        "• Нажми кнопку раздела в меню.\n"
        "• Для нумерологии отправь дату в формате ДД.ММ.ГГГГ.\n"
        "• Для Таро бот предложит символическую карту и вопрос для размышления.\n\n"
        "Команды: /start — меню, /help — помощь.\n"
        "Данные профиля не сохраняются в базе в этой версии.",
        reply_markup=MENU,
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    section = query.data

    if section == "numerology":
        context.user_data["awaiting_birthdate"] = True
        await query.message.reply_text(
            "🔢 Отправь дату рождения в формате ДД.ММ.ГГГГ.\n"
            "Например: 24.08.1995\n\n"
            "Используй дату только с разрешения человека, если это не твои данные."
        )
    elif section == "astrology":
        await query.message.reply_text(astrology_status(), reply_markup=MENU)
    elif section == "tarot":
        card = draw_reflection_card()
        await query.message.reply_text(
            f"🃏 Карта для размышления: {card['name']}\n\n"
            f"**Тема:** {card['theme']}\n\n"
            f"**Вопрос:** {card['question']}\n\n"
            "Это случайная символическая подсказка, а не предсказание.",
            parse_mode="Markdown",
            reply_markup=MENU,
        )
    elif section == "report":
        context.user_data["awaiting_birthdate"] = True
        context.user_data["report_mode"] = True
        await query.message.reply_text(
            "✨ Для демонстрационного комплексного разбора отправь дату рождения "
            "в формате ДД.ММ.ГГГГ. В эту версию пока входят нумерология и вопросы "
            "для саморефлексии; натальная карта ещё не рассчитывается."
        )
    elif section == "about":
        await query.message.reply_text(
            "Stella — прототип авторской системы самопознания.\n\n"
            "Модули независимы: это помогает не смешивать разные традиции без правил. "
            "Астрологические расчёты пока не подключены. Никакие эзотерические "
            "интерпретации не считаются научным доказательством характера или судьбы.",
            reply_markup=MENU,
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_birthdate"):
        await update.effective_message.reply_text(
            "Выбери раздел в меню или введи /help.", reply_markup=MENU
        )
        return

    raw_date = (update.effective_message.text or "").strip()
    try:
        number = life_path_number(raw_date)
    except ValueError:
        await update.effective_message.reply_text(
            "Не получилось прочитать дату. Используй формат ДД.ММ.ГГГГ, например 24.08.1995."
        )
        return

    context.user_data["awaiting_birthdate"] = False
    is_report = context.user_data.pop("report_mode", False)
    if is_report:
        text = build_report(raw_date, number, interpretation(number))
    else:
        text = (
            f"🔢 Число жизненного пути: {number}\n\n"
            f"{interpretation(number)}\n\n"
            "Нумерология — символическая традиция для размышления, а не научная оценка личности."
        )
    await update.effective_message.reply_text(text, reply_markup=MENU)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Необработанная ошибка при обработке обновления", exc_info=context.error)

def main() -> None:
    if not TOKEN:
        raise SystemExit(
            "Не найден TELEGRAM_BOT_TOKEN. Создай файл .env на основе .env.example "
            "и добавь токен от @BotFather."
        )
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    logger.info("Stella запускается")
    app.run_polling()

if __name__ == "__main__":
    main()
