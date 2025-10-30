# main.py
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests

# Инициализация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

PROMPT_TEMPLATE = """
Ты — помощник директора проектов в строительной компании. Твоя задача — на основе входных данных (протокол совещания, список просроченных замечаний, информация от технадзора) сформировать мотивирующее и вежливое, но жёсткое письмо/сообщение подрядчику с требованием устранить замечания и отчитаться.

Формат письма должен включать ТОЛЬКО следующие пункты:

1. **Адресат**: [имя подрядчика или ответственного лица]
2. **Суть проблемы**: [кратко: что не сделано, какие замечания просрочены, номера квартир/объектов]
3. **Последствия бездействия**: [влияние на репутацию компании, риск штрафов, срыв сроков передачи объекта]
4. **Конкретное требование**: [указать срок устранения, формат отчета — фото, акт, чек-лист]
5. **Призыв к действию**: [вежливый, но твёрдый призыв "включиться", "дать обратную связь до даты", "не допустить повторения"]

Тон: деловой, но с элементами давления. Не угрожать, но подчеркнуть важность. Использовать фразы: "важно для репутации", "требуется ваше немедленное вмешательство", "необходимо закрыть вопрос до [дата]".

Не добавляй пояснений, комментариев или лишнего текста. Только 5 пунктов.

Теперь обработай следующие входные данные:
"""

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    full_prompt = PROMPT_TEMPLATE + "\n\n" + user_text

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": full_prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.3}}
        )
        result = response.json()
        reply = result[0]['generated_text'].strip()
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Ошибка при генерации письма. Попробуйте позже.")

# Запуск
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()