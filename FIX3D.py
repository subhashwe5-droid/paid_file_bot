import telebot
from telebot import types
import uuid

# ⚙️ CONFIGURATION
API_TOKEN = "8360499891:AAFH8u_nD3R-yZEDO5V7xj1W921BiOv-TQo"
ADMIN_ID = 5840953778              # 👈 Owner chat ID (system me use hoga)
OWNER_USERNAME = "PA1Npy"  # 👈 Owner username (button ke liye)
BOT = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
BOT_USERNAME = BOT.get_me().username

# 🌐 Public Force Join Channels
REQUIRED_CHANNELS = ["P4INGOD", "P4XPY", "M0ZAN3"]

# 🧠 Data Storage
storage = {}
users = set()

# ✅ Check if user joined channels
def check_channels(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            member = BOT.get_chat_member(f"@{ch}", user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# 📎 Force Join Buttons
def send_force_join_buttons(chat_id, text="⚠️ Please join all channels first:"):
    markup = types.InlineKeyboardMarkup()
    for ch in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}"))
    markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_join"))
    BOT.send_message(chat_id, text, reply_markup=markup)

# 🔁 Recheck Join
@BOT.callback_query_handler(func=lambda call: call.data == "check_join")
def recheck_join(call):
    if check_channels(call.from_user.id):
        show_main_menu(call.message.chat.id)
    else:
        BOT.answer_callback_query(call.id, "❌ You still haven’t joined all channels!", show_alert=True)

# 🌟 Main Menu
def show_main_menu(chat_id):
    caption = (
        "👋 <b>HEY! I’M A FILE SHARING BOT BY PAIN ⚡</b>\n\n"
        "📦 I can turn your files, photos, or messages into sharable links.\n"
        "🚀 Send me anything & I’ll make a unique link for you!\n"
        "💡 Share that link with anyone — they can view it directly inside me.\n\n"
        "🌈 Fast ⚡ | Secure 🔒 | Easy 💫"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 OWNER", callback_data="owner_contact"))
    markup.add(types.InlineKeyboardButton("ℹ️ ABOUT", callback_data="about_bot"))
    markup.add(types.InlineKeyboardButton("🔗 GENERATE LINK", callback_data="generate_link"))
    BOT.send_message(chat_id, caption, reply_markup=markup)

# 👑 OWNER Button → clickable username
@BOT.callback_query_handler(func=lambda call: call.data == "owner_contact")
def owner_info(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💬 Message Owner", url=f"https://t.me/{OWNER_USERNAME}")
    )
    BOT.send_message(call.message.chat.id, "👑 Tap the button below to message the owner directly 👇", reply_markup=markup)

# ℹ️ About Section
@BOT.callback_query_handler(func=lambda call: call.data == "about_bot")
def about_section(call):
    text = (
        "🤖 <b>ABOUT THIS BOT</b>\n\n"
        f"👑 Owner: <a href='https://t.me/{OWNER_USERNAME}'>Tap Here</a>\n"
        f"💠 Bot Name: @{BOT_USERNAME}\n\n"
        "📌 <b>Features:</b>\n"
        "• 🔗 Generate sharable links for files & text\n"
        "• 🧠 Auto detect join\n"
        "• 💬 Broadcast & user stats (admin only)\n"
        "• 🚫 No group spam\n"
        "• ⚡ Fast, Secure, & User Friendly!"
    )
    BOT.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", disable_web_page_preview=True)

# 🔗 Generate Link Button
@BOT.callback_query_handler(func=lambda call: call.data == "generate_link")
def generate_prompt(call):
    BOT.send_message(call.message.chat.id, "📨 Send me a file, photo, or text to generate a sharable link.")

# 🎯 Start Command
@BOT.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    users.add(user_id)

    if message.chat.type != "private":
        return

    # 🔔 Notify owner on new user
    if user_id != ADMIN_ID:
        name = message.from_user.first_name or "Unknown"
        username = f"@{message.from_user.username}" if message.from_user.username else "❌ No username"
        BOT.send_message(
            ADMIN_ID,
            f"💥 <b>New User Started Bot!</b>\n\n👤 Name: {name}\n🧩 Username: {username}\n🆔 ID: <code>{user_id}</code>"
        )

    # 🔹 Handle /start <unique_id>
    args = message.text.split()
    if len(args) > 1:
        unique_id = args[1]
        if unique_id in storage:
            data = storage[unique_id]
            if data["type"] == "text":
                BOT.send_message(user_id, data["data"])
            elif data["type"] == "photo":
                BOT.send_photo(user_id, data["file_id"])
            elif data["type"] == "document":
                BOT.send_document(user_id, data["file_id"])
            return
        else:
            BOT.send_message(user_id, "❌ This link has expired or is invalid.")
            return

    if not check_channels(user_id):
        send_force_join_buttons(user_id)
        return

    show_main_menu(user_id)

# 🧩 Generate Link System
def generate_unique_link(message, file_type, file_id_or_text):
    unique_id = str(uuid.uuid4())
    storage[unique_id] = {"type": file_type, "file_id": file_id_or_text}
    link = f"https://t.me/{BOT_USERNAME}?start={unique_id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 Share Link", switch_inline_query=link))
    BOT.send_message(message.chat.id, f"✅ <b>Your sharable link is ready!</b>\n\n🔗 {link}", reply_markup=markup)

# 📝 Text Handler
@BOT.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.type != "private":
        return
    if not check_channels(message.from_user.id):
        send_force_join_buttons(message.chat.id)
        return
    generate_unique_link(message, "text", message.text)

# 🖼 Photo Handler
@BOT.message_handler(content_types=["photo"])
def handle_photo(message):
    if message.chat.type != "private":
        return
    if not check_channels(message.from_user.id):
        send_force_join_buttons(message.chat.id)
        return
    generate_unique_link(message, "photo", message.photo[-1].file_id)

# 📄 Document Handler
@BOT.message_handler(content_types=["document"])
def handle_doc(message):
    if message.chat.type != "private":
        return
    if not check_channels(message.from_user.id):
        send_force_join_buttons(message.chat.id)
        return
    generate_unique_link(message, "document", message.document.file_id)

# ♻️ Run Bot
BOT.infinity_polling()