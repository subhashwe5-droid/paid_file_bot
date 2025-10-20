import subprocess
import sys
import os

# --------------------------
# ✅ Required Python Modules
required_modules = ["pyTelegramBotAPI", "uuid"]

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"Installing {module} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# --------------------------
# ✅ All dependencies installed, ab bot import karte hain
import telebot
from telebot import types
import uuid
import datetime

# ⚙️ CONFIGURATION
API_TOKEN = "8360499891:AAFH8u_nD3R-yZEDO5V7xj1W921BiOv-TQo"  # apna bot token yahan
ADMIN_ID = 5840953778              # apna ID yahan
OWNER_USERNAME = "PA1Npy"

BOT = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
BOT_USERNAME = BOT.get_me().username if BOT.get_me() else "BOT_USERNAME"

# 🌐 Force Join Channels
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
def send_force_join_buttons(chat_id, text="⚠️ Pehle sabhi channels join karo:"):
    markup = types.InlineKeyboardMarkup()
    for ch in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}"))
    markup.add(types.InlineKeyboardButton("✅ Join Kar Liya", callback_data="check_join"))
    BOT.send_message(chat_id, text, reply_markup=markup)

# 🔁 Recheck Join (with pending file unlock)
@BOT.callback_query_handler(func=lambda call: call.data == "check_join")
def recheck_join(call):
    user_id = call.from_user.id

    # agar pending link save hai
    if user_id in storage and isinstance(storage[user_id], dict) and "pending_id" in storage[user_id]:
        unique_id = storage[user_id]["pending_id"]
    else:
        unique_id = None

    if check_channels(user_id):
        if unique_id and unique_id in storage:
            data = storage[unique_id]
            if data["type"] == "text":
                BOT.send_message(user_id, data["data"])
            elif data["type"] == "photo":
                BOT.send_photo(user_id, data["file_id"])
            elif data["type"] == "document":
                BOT.send_document(user_id, data["file_id"])
            del storage[user_id]
        else:
            show_main_menu(call.message.chat.id)
    else:
        BOT.answer_callback_query(call.id, "❌ Abhi bhi join nahi kiya!", show_alert=True)

# 🌟 Main Menu
def show_main_menu(chat_id):
    caption = (
        "👋 <b>HEY! I’M A FILE SHARING BOT BY PAIN ⚡</b>\n\n"
        "📦 Send me any file, photo, or message & I’ll generate a sharable link.\n"
        "🚀 Fast ⚡ Secure 🔒 Easy 💫"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 OWNER", callback_data="owner_contact"))
    markup.add(types.InlineKeyboardButton("ℹ️ ABOUT", callback_data="about_bot"))
    markup.add(types.InlineKeyboardButton("🔗 GENERATE LINK", callback_data="generate_link"))
    BOT.send_message(chat_id, caption, reply_markup=markup)

# 👑 OWNER Button
@BOT.callback_query_handler(func=lambda call: call.data == "owner_contact")
def owner_info(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Message Owner", url=f"https://t.me/{OWNER_USERNAME}"))
    BOT.send_message(call.message.chat.id, "👑 Tap below to contact the owner 👇", reply_markup=markup)

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
        "• 💬 Detailed user notifications\n"
        "• ⚡ Fast, Secure, & User Friendly!"
    )
    BOT.edit_message_text(text, call.message.chat.id, call.message.message_id, disable_web_page_preview=True)

# 🔗 Generate Link Button
@BOT.callback_query_handler(func=lambda call: call.data == "generate_link")
def generate_prompt(call):
    BOT.send_message(call.message.chat.id, "📨 Send me any file, photo, or text to generate a sharable link.")

# 🎯 Start Command
@BOT.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    user_id = user.id
    users.add(user_id)

    if message.chat.type != "private":
        return

    # 🧾 Extended Info for Owner
    if user_id != ADMIN_ID:
        try:
            chat_info = BOT.get_chat(user_id)
            bio = getattr(chat_info, "bio", "❌ No bio")
        except:
            bio = "❌ Bio unavailable"

        is_premium = "✅ Yes" if getattr(user, "is_premium", False) else "❌ No"
        is_bot = "✅ Yes" if user.is_bot else "❌ No"
        lang = user.language_code or "❌ Unknown"
        username = f"@{user.username}" if user.username else "❌ No username"
        joined_by_link = "✅ Yes" if len(message.text.split()) > 1 else "❌ No"
        timestamp = datetime.datetime.utcfromtimestamp(message.date).strftime("%Y-%m-%d %H:%M:%S")

        BOT.send_message(
            ADMIN_ID,
            f"💥 <b>New User Started Bot!</b>\n\n"
            f"👤 <b>Name:</b> {user.first_name or 'Unknown'}\n"
            f"🧩 <b>Username:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"🌐 <b>Language:</b> {lang}\n"
            f"💎 <b>Premium:</b> {is_premium}\n"
            f"🤖 <b>Bot Account:</b> {is_bot}\n"
            f"📅 <b>Started:</b> {timestamp}\n"
            f"🔗 <b>Via Link:</b> {joined_by_link}\n"
            f"📝 <b>Bio:</b> {bio}"
        )

    # Normal start
    if not check_channels(user_id):
        send_force_join_buttons(user_id)
        return

    show_main_menu(user_id)

# 🧩 Generate Link System
def generate_unique_link(message, file_type, file_id_or_text):
    unique_id = str(uuid.uuid4())
    storage[unique_id] = {"type": file_type, "file_id_or_text": file_id_or_text}
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