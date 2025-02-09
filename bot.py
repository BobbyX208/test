from flask import Flask, request
from telebot import TeleBot
import config
import database
from keyboards import get_admin_keyboard, get_user_keyboard
from handlers.user import register_handlers as user_handlers
from handlers.admin import register_handlers as admin_handlers

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
bot = TeleBot(config.BOT_TOKEN)

# Initialize database
database.init_db()

# Register handlers
admin_handlers(bot)
user_handlers(bot)

# Root route to avoid 404 errors
@app.route('/')
def home():
    return """
    <h1>Welcome to the Your TelegramBot!</h1>
    <p>This is a web app hosting a Telegram bot. If you're seeing this,it means that the bot is running correctly and you have made Mr Anderson proud.</p>
    <p>To interact with the bot, visit <a href="https://t.me/bobmods_bot">Telegram</a>.</p>
    """

# Webhook route for Koyeb
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    bot.process_new_updates([update])
    return 'ok', 200

# Set webhook on startup
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{config.WEBHOOK_URL}/webhook")

# Run set_webhook when the app starts
set_webhook()

# Start bot with Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)