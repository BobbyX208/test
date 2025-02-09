from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# User Keyboard
def get_user_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    # First row
    keyboard.add(
        KeyboardButton("🛠 Request Mod"),
        KeyboardButton("⚠️ Report Error")
    )
    
    # Second row
    keyboard.add(
        KeyboardButton("💡 Suggest Features"),
        KeyboardButton("📩 Chat with Admin")
    )
    
    # Third row
    keyboard.add(KeyboardButton("🔙 Back"))
    
    return keyboard

# Admin Keyboard
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    # First row
    keyboard.add(
        KeyboardButton("📨 Reply to Chat"),
        KeyboardButton("📢 Broadcast Message")
    )
    
    # Second row
    keyboard.add(
        KeyboardButton("👥 View All Users"),
        KeyboardButton("📊 View Stats")
    )
    
    # Third row
    keyboard.add(KeyboardButton("🔙 Back"))
    
    return keyboard

# Inline Keyboard for User Selection (Admin Reply)
def get_user_selection_keyboard(users):
    keyboard = InlineKeyboardMarkup()
    
    for user in users:
        keyboard.add(
            InlineKeyboardButton(
                text=f"👤 {user[1]} (ID: {user[0]})",
                callback_data=f"reply_to_{user[0]}"
            )
        )
    
    return keyboard