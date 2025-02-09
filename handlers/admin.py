from telebot import types
import config
import database
from keyboards import get_admin_keyboard

# Temporary storage for admin replies
admin_reply_context = {}

def register_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "📢 Broadcast Message")
    def broadcast_message(message):
        bot.send_message(message.chat.id, "Type the broadcast message:")
        bot.register_next_step_handler(message, process_broadcast)

    def process_broadcast(message):
        users = database.get_all_users()
        if not users:
            bot.send_message(message.chat.id, "❌ No users to broadcast to.")
            return

        for user in users:
            bot.send_message(
                user[0],
                f"✅ **Admin Announcement**\n\n{message.text}"
            )
        bot.send_message(message.chat.id, f"📢 Broadcast sent to {len(users)} users!")

    @bot.message_handler(func=lambda m: m.text == "👥 View All Users")
    def view_users(message):
        users = database.get_all_users()
        if not users:
            bot.send_message(message.chat.id, "❌ No users registered.")
            return

        user_list = "\n".join([f"👤 {u[1]} (ID: {u[0]})" for u in users])
        bot.send_message(
            message.chat.id,
            f"📊 Registered Users ({len(users)}):\n{user_list}"
        )

    @bot.message_handler(func=lambda m: m.text == "📊 View Stats")
    def view_stats(message):
        total_users = database.get_user_count()
        active_requests = database.get_active_requests()
        
        bot.send_message(
            message.chat.id,
            f"📊 **Bot Stats**\n\n"
            f"👥 Total Users: {total_users}\n"
            f"📨 Active Requests: {active_requests}"
        )

    @bot.message_handler(func=lambda m: m.text == "📨 Reply to Chat")
    def reply_to_chat(message):
        users = database.get_all_users()
        if not users:
            bot.send_message(message.chat.id, "❌ No users to reply to.")
            return

        markup = types.InlineKeyboardMarkup()
        for user in users:
            btn = types.InlineKeyboardButton(
                text=f"👤 {user[1]} (ID: {user[0]})",
                callback_data=f"reply_to_{user[0]}"
            )
            markup.add(btn)
        
        bot.send_message(
            message.chat.id,
            "Select a user to reply:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reply_to_"))
    def select_user_callback(call):
        user_id = int(call.data.split("_")[-1])
        admin_reply_context[call.message.chat.id] = user_id  # Store selected user
        
        msg = bot.send_message(
            call.message.chat.id,
            "💬 Type your reply:"
        )
        bot.register_next_step_handler(msg, process_admin_reply)

    def process_admin_reply(message):
        admin_chat_id = message.chat.id
        user_id = admin_reply_context.get(admin_chat_id)
        
        if not user_id:
            bot.send_message(admin_chat_id, "❌ Error: User not found.")
            return

        # Send to user with verified badge
        bot.send_message(
            user_id,
            f"✅ **Admin Reply**\n\n{message.text}"
        )
        
        # Confirm to admin
        bot.send_message(
            admin_chat_id,
            f"📩 Reply sent to user {user_id}!"
        )
        
        # Clear context
        del admin_reply_context[admin_chat_id]