import os
import sqlite3
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Load environment variables from Replit Secrets
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Initialize database
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Function to save user to the database
def save_user(chat_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username))
    conn.commit()
    conn.close()

# Function to get all users
def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "Unknown"
    
    save_user(chat_id, username)  # Save user in DB

    if chat_id == ADMIN_CHAT_ID:
        keyboard = [
            [InlineKeyboardButton("Reply to Chats", callback_data='reply_chats')],
            [InlineKeyboardButton("Broadcast Message", callback_data='broadcast')],
            [InlineKeyboardButton("Help", callback_data='admin_help')]
        ]
    else:
        keyboard = [[InlineKeyboardButton("Chat with Admin", callback_data='chat_admin')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    await query.answer()

    if query.data == 'chat_admin':
        await query.edit_message_text(text="Send your message, and the admin will respond.")
        context.user_data['chatting_with_admin'] = True

    elif query.data == 'reply_chats' and chat_id == ADMIN_CHAT_ID:
        users = get_all_users()
        if not users:
            await query.edit_message_text("No users have interacted with the bot yet.")
            return

        keyboard = [[InlineKeyboardButton(f"{user[1]}", callback_data=f"reply_{user[0]}")] for user in users]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a user to reply:", reply_markup=reply_markup)

    elif query.data.startswith("reply_") and chat_id == ADMIN_CHAT_ID:
        target_user = int(query.data.split("_")[1])
        context.user_data['reply_target'] = target_user
        await query.edit_message_text("Enter your reply message:")

    elif query.data == 'broadcast' and chat_id == ADMIN_CHAT_ID:
        context.user_data['broadcast_mode'] = True
        await query.edit_message_text("Enter your broadcast message:")

    elif query.data == 'admin_help' and chat_id == ADMIN_CHAT_ID:
        help_text = """📌 *Bot Features:*
- Reply to user messages
- Broadcast messages to all users
- View list of all users
- Automatic user saving in database"""
        await query.edit_message_text(help_text, parse_mode="Markdown")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_message = update.message.text
    username = update.message.from_user.username or "Unknown"

    if chat_id == ADMIN_CHAT_ID and 'reply_target' in context.user_data:
        target_user = context.user_data.pop('reply_target')
        await context.bot.send_message(target_user, f"✅ *Admin Reply:* {user_message}", parse_mode="Markdown")
        await update.message.reply_text("Reply sent successfully!")

    elif chat_id == ADMIN_CHAT_ID and context.user_data.get('broadcast_mode'):
        users = get_all_users()
        for user in users:
            try:
                await context.bot.send_message(user[0], f"📢 *Broadcast:* {user_message}", parse_mode="Markdown")
            except:
                pass  # Skip if user blocked bot
        await update.message.reply_text("Broadcast message sent to all users.")
        context.user_data['broadcast_mode'] = False

    elif context.user_data.get('chatting_with_admin'):
        await context.bot.send_message(ADMIN_CHAT_ID, f"📩 *Message from @{username}:* {user_message}")
        await update.message.reply_text("Your message has been sent to the admin.")

# Main function
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
