import os
from dotenv import load_dotenv
from supabase import create_client, Client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env
load_dotenv()

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Function to add a new user to the Supabase database
async def add_user_to_db(chat_id, username, first_name, last_name):
    user_data = {
        "chat_id": chat_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name
    }
    response = supabase.table('users').upsert(user_data).execute()
    return response

# Function to get a list of all users from the database
async def get_all_users():
    response = supabase.table('users').select('*').execute()
    return response.data

# Start command - Add user to database if not already in the system
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    # Add user to Supabase database
    await add_user_to_db(chat_id, username, first_name, last_name)

    keyboard = [
        [InlineKeyboardButton("Request Mod", callback_data='request_mod')],
        [InlineKeyboardButton("Report Error", callback_data='report_error')],
        [InlineKeyboardButton("Suggest Feature", callback_data='suggest_feature')],
        [InlineKeyboardButton("Chat with Admin", callback_data='chat_admin')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"Welcome {first_name} {last_name}! Please choose an option:", reply_markup=reply_markup)

# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'request_mod':
        await query.edit_message_text(text="Please send details of the mod you want.")
        context.user_data['awaiting_mod_request'] = True
    elif query.data == 'report_error':
        await query.edit_message_text(text="Please describe the error you encountered.")
        context.user_data['awaiting_error_report'] = True
    elif query.data == 'suggest_feature':
        await query.edit_message_text(text="Please describe your feature suggestion.")
        context.user_data['awaiting_feature_suggestion'] = True
    elif query.data == 'chat_admin':
        await query.edit_message_text(text="Send your message, and the admin will respond.")
        context.user_data['chatting_with_admin'] = True

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.message.chat_id
    username = update.message.from_user.username or "Unknown User"

    if context.user_data.get('awaiting_mod_request'):
        await context.bot.send_message(ADMIN_CHAT_ID, f"🔹 *Mod Request* from @{username}:\n{user_message}")
        await update.message.reply_text("Your mod request has been sent to the admin.")
        context.user_data['awaiting_mod_request'] = False

    elif context.user_data.get('awaiting_error_report'):
        await context.bot.send_message(ADMIN_CHAT_ID, f"⚠ *Error Report* from @{username}:\n{user_message}")
        await update.message.reply_text("Your error report has been sent to the admin.")
        context.user_data['awaiting_error_report'] = False

    elif context.user_data.get('awaiting_feature_suggestion'):
        await context.bot.send_message(ADMIN_CHAT_ID, f"💡 *Feature Suggestion* from @{username}:\n{user_message}")
        await update.message.reply_text("Your feature suggestion has been sent to the admin.")
        context.user_data['awaiting_feature_suggestion'] = False

    elif context.user_data.get('chatting_with_admin'):
        await context.bot.send_message(ADMIN_CHAT_ID, f"📩 *Message from @{username}*:\n{user_message}")
        await update.message.reply_text("Your message has been sent to the admin.")

# Admin Commands:
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == ADMIN_CHAT_ID:
        users = await get_all_users()
        user_list = "\n".join([f"{user['username']} ({user['chat_id']})" for user in users])
        await update.message.reply_text(f"List of users:\n{user_list}")
    else:
        await update.message.reply_text("You are not authorized to view this information.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == ADMIN_CHAT_ID:
        message = ' '.join(context.args)
        users = await get_all_users()
        for user in users:
            await context.bot.send_message(user['chat_id'], message)
        await update.message.reply_text("Message sent to all users.")
    else:
        await update.message.reply_text("You are not authorized to send messages to all users.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == ADMIN_CHAT_ID:
        help_text = (
            "Bot Features:\n"
            "- /start: Register and interact with the bot.\n"
            "- /list_users: List all users (admin only).\n"
            "- /broadcast <message>: Send a message to all users (admin only).\n"
            "- /help: View available bot commands (admin only).\n"
            "- /request_mod: Request a moderator.\n"
            "- /report_error: Report an error.\n"
            "- /suggest_feature: Suggest a new feature.\n"
            "- /chat_admin: Chat with the admin."
        )
        await update.message.reply_text(help_text)
    else:
        await update.message.reply_text("You are not authorized to view help information.")

# Main function
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Adding handlers for commands and buttons
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Admin commands
    app.add_handler(CommandHandler("list_users", list_users))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("help", help))

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
