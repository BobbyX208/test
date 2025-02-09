from telebot import types
import config
import database
from keyboards import get_user_keyboard

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.chat.id
        username = message.from_user.username or "NoUsername"
        
        # Add user to database
        database.add_user(user_id, username)
        
        # Send welcome message with keyboard
        bot.send_message(
            user_id,
            "Welcome! Use the buttons below to interact with the bot.",
            reply_markup=get_user_keyboard()
        )

    # Suggest Features
    @bot.message_handler(func=lambda message: message.text == "💡 Suggest Features")
    def suggest_features(message):
        bot.send_message(message.chat.id, "Please describe your feature suggestion:")
        bot.register_next_step_handler(message, lambda m: _send_to_admin(m, "💡 Feature Suggestion"))

    # Report Error
    @bot.message_handler(func=lambda message: message.text == "⚠️ Report Error")
    def report_error(message):
        bot.send_message(message.chat.id, "Please describe the error you encountered:")
        bot.register_next_step_handler(message, lambda m: _send_to_admin(m, "⚠️ Error Report"))

    # Request Mod
    @bot.message_handler(func=lambda message: message.text == "🛠 Request Mod")
    def request_mod(message):
        bot.send_message(message.chat.id, "Please provide details about the mod you want:")
        bot.register_next_step_handler(message, lambda m: _send_to_admin(m, "🛠 Mod Request"))

    # Chat with Admin
    @bot.message_handler(func=lambda message: message.text == "📩 Chat with Admin")
    def chat_with_admin(message):
        bot.send_message(message.chat.id, "Type your message to the admin:")
        bot.register_next_step_handler(message, lambda m: _send_to_admin(m, "📩 User Message"))

    # Back Button
    @bot.message_handler(func=lambda message: message.text == "🔙 Back")
    def back_user(message):
        bot.send_message(message.chat.id, "Menu cleared.", reply_markup=types.ReplyKeyboardRemove())

    # Media Handler for Users
    @bot.message_handler(content_types=['photo', 'document', 'video'])
    def handle_user_media(message):
        # Forward media to admin
        bot.send_message(
            config.ADMIN_ID,
            f"📤 Media from User {message.from_user.id} (@{message.from_user.username})"
        )
        bot.forward_message(config.ADMIN_ID, message.chat.id, message.message_id)
        
        # Confirm to user
        bot.send_message(message.chat.id, "✅ Media forwarded to admin.")

    # Helper function to send labeled messages to admin
    def _send_to_admin(message, action_label):
        user_info = f"User ID: {message.from_user.id}\nUsername: @{message.from_user.username}"
        admin_msg = f"{action_label}:\n\n{message.text}\n\n{user_info}"
        
        # Send to admin
        bot.send_message(config.ADMIN_ID, admin_msg)
        
        # Confirm to user
        bot.send_message(message.chat.id, f"✅ Sent to admin: {action_label}")
        
        # Log message in database
        database.add_message(message.from_user.id, config.ADMIN_ID, message.text)