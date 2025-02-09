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

# Webhook route for Koyeb
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    bot.process_new_updates([update])
    return 'ok', 200

# Start bot with Flask
if __name__ == "__main__":
    # Set webhook for Koyeb
    bot.remove_webhook()
    bot.set_webhook(url=f"{config.WEBHOOK_URL}/webhook")
    
    # Start Flask app
    app.run(host="0.0.0.0", port=8080)