import telebot
from telebot import types
import time
import os

# ---------- CONFIG ----------
BOT_TOKEN = "8599410307:AAHTxhIxiDQFMr0urdQNT_CRCzCQw2Jqdko"
ADMIN_ID = 5840953778
FORWARD_CHANNEL = "@P4XPY1"

DEVELOPER = "@PA1Npy"
UPDATE = "@P4XPY"

bot = telebot.TeleBot(BOT_TOKEN)

# USER DATA
user_file = {}
user_thumb = {}
user_rename = {}
user_expiry = {}
user_caption = {}
banned_users = set()

# ---------- USER DATABASE ----------
def save_user(uid):
    try:
        if not os.path.exists("users.txt"):
            open("users.txt", "w").close()

        with open("users.txt", "r") as f:
            all_ids = f.read().splitlines()

        if str(uid) not in all_ids:
            with open("users.txt", "a") as f:
                f.write(str(uid) + "\n")
    except:
        pass

def load_users():
    if not os.path.exists("users.txt"):
        return []
    with open("users.txt", "r") as f:
        return f.read().splitlines()

# ---------- WELCOME ----------
def send_welcome(chat_id, name):
    save_user(chat_id)
    if chat_id in banned_users:
        return bot.send_message(chat_id, "🚫 You are banned from using this bot")

    btn = types.InlineKeyboardMarkup()
    btn.row(
        types.InlineKeyboardButton("📂 Upload File", callback_data="upload"),
        types.InlineKeyboardButton("ℹ About", callback_data="about")
    )
    btn.row(
        types.InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEVELOPER.replace('@','')}"),
        types.InlineKeyboardButton("🔔 Updates", url=f"https://t.me/{UPDATE.replace('@','')}")
    )
    if chat_id == ADMIN_ID:
        btn.row(types.InlineKeyboardButton("🛠 Admin Panel", callback_data="admin"))

    msg = f"""
┏━━━━━━━━━━━━━━━┓
⚡ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥 ⚡
┗━━━━━━━━━━━━━━━┛

👋 Hᴇʏ {name}!
Yᴏᴜʀ ғɪʟᴇ ᴍᴏᴅɪғɪᴄᴀᴛɪᴏɴ ᴘʀᴏᴄᴇꜱꜱ ɪꜱ ʀᴇᴀᴅʏ ✅

💻 Wɪᴛʜ ᴍᴇ ʏᴏᴜ ᴄᴀɴ:
✔ Aᴅᴅ Tʜᴜᴍʙɴᴀɪʟ
✔ Cʜᴀɴɢᴇ Fɪʟᴇ Nᴀᴍᴇ
✔ Aᴅᴅ Cᴀᴘᴛɪᴏɴ
✔ Aᴜᴛᴏ Eᴜᴘɪʀʏ Sʏꜱᴛᴇᴍ

📩 Jᴜꜱᴛ sᴇɴᴅ ʏᴏᴜʀ .ᴘʏ ғɪʟᴇ!
"""
    bot.send_message(chat_id, msg, reply_markup=btn)

@bot.message_handler(commands=['start'])
def start(message):
    send_welcome(message.chat.id, message.from_user.first_name)

# ---------- ABOUT ----------
@bot.callback_query_handler(func=lambda c: c.data == "about")
def about(call):
    btn = types.InlineKeyboardMarkup()
    btn.row(
        types.InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEVELOPER.replace('@','')}"),
        types.InlineKeyboardButton("🔔 Updates", url=f"https://t.me/{UPDATE.replace('@','')}")
    )
    if call.message.chat.id == ADMIN_ID:
        btn.row(types.InlineKeyboardButton("🛠 Admin Panel", callback_data="admin"))

    bot.send_message(call.message.chat.id, f"""
✨ About This Bot

This bot professionally customizes Python .py files:
• 🖼 Add thumbnail preview
• ✍️ Edit caption
• 📂 Rename file
• ⏳ Inject expiry guard inside file

Send any file to begin.
""", reply_markup=btn)

# ===================== ADMIN PANEL =====================
@bot.callback_query_handler(func=lambda c: c.data == "admin")
def admin(call):
    if call.message.chat.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ You are not admin")

    btn = types.InlineKeyboardMarkup()
    btn.row(
        types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
        types.InlineKeyboardButton("📁 Users", callback_data="users")
    )
    btn.row(
        types.InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
        types.InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
    )
    btn.row(
        types.InlineKeyboardButton("📊 Bot Stats", callback_data="stats")
    )
    btn.row(
        types.InlineKeyboardButton("📜 Logs", callback_data="logs")
    )
    bot.send_message(call.message.chat.id, "✅ Admin Panel Opened ✅", reply_markup=btn)

# ---------- USERS LIST ----------
@bot.callback_query_handler(func=lambda c: c.data == "users")
def show_users(call):
    if call.message.chat.id != ADMIN_ID: return
    users = load_users()
    bot.send_message(call.message.chat.id, f"👤 Total Users: {len(users)}")

# ---------- STATS ----------
@bot.callback_query_handler(func=lambda c: c.data == "stats")
def bot_stats(call):
    users = load_users()
    bot.send_message(call.message.chat.id, f"""
📊 **BOT STATS**
👤 Total Users: {len(users)}
🚫 Banned Users: {len(banned_users)}
""")

# ---------- BAN USER ----------
@bot.callback_query_handler(func=lambda c: c.data == "ban_user")
def ask_ban(call):
    bot.send_message(call.message.chat.id, "🚫 Send User ID To Ban:")
    user_caption[call.message.chat.id] = "BAN_WAIT"

@bot.message_handler(func=lambda m: user_caption.get(m.chat.id) == "BAN_WAIT")
def do_ban(message):
    uid = message.text
    banned_users.add(int(uid))
    user_caption.pop(message.chat.id, None)
    bot.send_message(message.chat.id, f"✅ Banned User: {uid}")

# ---------- UNBAN ----------
@bot.callback_query_handler(func=lambda c: c.data == "unban_user")
def unban_menu(call):
    bot.send_message(call.message.chat.id, "✅ Send User ID to Unban:")
    user_caption[call.message.chat.id] = "UNBAN_WAIT"

@bot.message_handler(func=lambda m: user_caption.get(m.chat.id) == "UNBAN_WAIT")
def do_unban(message):
    uid = message.text
    try:
        banned_users.remove(int(uid))
        bot.send_message(message.chat.id, f"✅ Unbanned User: {uid}")
    except:
        bot.send_message(message.chat.id, "❌ User not in ban list")
    user_caption.pop(message.chat.id, None)

# ---------- BROADCAST ----------
@bot.callback_query_handler(func=lambda c: c.data == "broadcast")
def ask_broadcast(call):
    bot.send_message(call.message.chat.id, "📢 Send broadcast message now:")
    user_caption[call.message.chat.id] = "BROADCAST_WAIT"

@bot.message_handler(func=lambda m: user_caption.get(m.chat.id) == "BROADCAST_WAIT")
def do_broadcast(message):
    users = load_users()
    sent = 0
    for uid in users:
        try:
            bot.send_message(int(uid), message.text)
            sent += 1
        except:
            pass
    bot.send_message(ADMIN_ID, f"✅ Broadcast sent to {sent} users")
    user_caption.pop(message.chat.id, None)

# ---------- LOGS ----------
@bot.callback_query_handler(func=lambda c: c.data == "logs")
def logs(call):
    if not os.path.exists("logs.txt"):
        return bot.send_message(call.message.chat.id, "📜 No logs yet")

    with open("logs.txt", "r") as f:
        data = f.read()

    bot.send_message(call.message.chat.id, f"📜 Logs:\n\n{data}" if data else "📜 No logs")

# ===================== FILE SYSTEM =====================
@bot.callback_query_handler(func=lambda c: c.data == "upload")
def ask_upload(call):
    bot.send_message(call.message.chat.id, "📁 Send your .py file now")

@bot.message_handler(content_types=['document'])
def receive_file(message):
    if message.chat.id in banned_users:
        return bot.reply_to(message, "🚫 You are banned")

    doc = message.document
    if not doc.file_name.endswith(".py"):
        return bot.reply_to(message, "❌ Only .py files allowed")

    cid = message.chat.id
    save_user(cid)

    user_file[cid] = doc
    user_thumb.pop(cid, None)
    user_rename.pop(cid, None)
    user_expiry.pop(cid, None)
    user_caption.pop(cid, None)

    with open("logs.txt", "a") as f:
        f.write(f"User {cid} sent file: {doc.file_name}\n")

    btn = types.InlineKeyboardMarkup()
    btn.row(
        types.InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb"),
        types.InlineKeyboardButton("✏ Rename", callback_data="rename")
    )
    btn.row(
        types.InlineKeyboardButton("📝 Caption", callback_data="caption"),
        types.InlineKeyboardButton("⏳ Expiry", callback_data="expiry")
    )
    btn.row(
        types.InlineKeyboardButton("📦 DOWNLOAD FILE", callback_data="finish")
    )

    bot.reply_to(message, "📥 FILE RECEIVED ✅\nSelect Options:", reply_markup=btn)

# ---------- THUMBNAIL ----------
@bot.callback_query_handler(func=lambda c: c.data == "thumb")
def ask_thumb(call):
    cid = call.message.chat.id
    user_thumb[cid] = "WAIT"
    bot.send_message(cid, "📸 Send thumbnail image now")

@bot.message_handler(content_types=['photo'])
def save_thumb(message):
    cid = message.chat.id
    if user_thumb.get(cid) != "WAIT":
        return

    file = bot.get_file(message.photo[-1].file_id)
    d = bot.download_file(file.file_path)
    path = f"thumb_{cid}.jpg"
    with open(path, "wb") as f:
        f.write(d)
    user_thumb[cid] = path
    bot.reply_to(message, "✅ Thumbnail saved")

# ---------- RENAME ----------
@bot.callback_query_handler(func=lambda c: c.data == "rename")
def ask_rename(call):
    cid = call.message.chat.id
    user_rename[cid] = "WAIT"
    bot.send_message(cid, "✏ Send new file name (must end .py)")

@bot.message_handler(func=lambda m: user_rename.get(m.chat.id) == "WAIT")
def save_name(message):
    name = message.text
    if not name.endswith(".py"):
        return bot.reply_to(message, "❌ Must end with .py")
    user_rename[message.chat.id] = name
    bot.reply_to(message, f"✅ Name saved: {name}")

# ---------- CAPTION ----------
@bot.callback_query_handler(func=lambda c: c.data == "caption")
def ask_caption(call):
    cid = call.message.chat.id
    user_caption[cid] = "WAIT2"
    bot.send_message(cid, "📝 Send caption text")

@bot.message_handler(func=lambda m: user_caption.get(m.chat.id) == "WAIT2")
def save_caption(message):
    user_caption[message.chat.id] = message.text
    bot.reply_to(message, "✅ Caption saved")

# ---------- EXPIRY ----------
@bot.callback_query_handler(func=lambda c: c.data == "expiry")
def expiry_menu(call):
    btn = types.InlineKeyboardMarkup()
    btn.row(
        types.InlineKeyboardButton("1h", callback_data="exp_3600"),
        types.InlineKeyboardButton("12h", callback_data="exp_43200")
    )
    btn.row(
        types.InlineKeyboardButton("1d", callback_data="exp_86400"),
        types.InlineKeyboardButton("3d", callback_data="exp_259200")
    )
    btn.row(
        types.InlineKeyboardButton("7d", callback_data="exp_604800"),
        types.InlineKeyboardButton("1m", callback_data="exp_2592000")
    )
    bot.send_message(call.message.chat.id, "⏳ Select expiry:", reply_markup=btn)

@bot.callback_query_handler(func=lambda c: c.data.startswith("exp_"))
def set_expiry(call):
    secs = int(call.data.replace("exp_", ""))
    user_expiry[call.message.chat.id] = secs
    bot.answer_callback_query(call.id, "✅ Expiry Set")

# ---------- FINAL SEND ----------
@bot.callback_query_handler(func=lambda c: c.data == "finish")
def finish(call):
    cid = call.message.chat.id
    doc = user_file.get(cid)
    if not doc:
        return bot.send_message(cid, "❌ No file found")

    file_info = bot.get_file(doc.file_id)
    code = bot.download_file(file_info.file_path).decode("utf-8")

    # Add expiry to code
    if cid in user_expiry:
        exp = int(time.time()) + user_expiry[cid]
        code = f"""
import time
if time.time() > {exp}:
    print("❌ Script expired")
    exit()
""" + code

    filename = user_rename.get(cid, doc.file_name)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    cap = user_caption.get(cid)
    thumb = user_thumb.get(cid)

    bot.send_document(
        cid,
        open(filename, "rb"),
        caption=cap,
        thumb=open(thumb, "rb") if thumb else None
    )

    bot.send_message(
        FORWARD_CHANNEL,
        f"📤 New File Uploaded\n👤 User: {call.from_user.first_name}\n🆔 ID: {cid}"
    )
    bot.send_document(
        FORWARD_CHANNEL,
        open(filename, "rb"),
        caption=cap,
        thumb=open(thumb, "rb") if thumb else None
    )

    bot.send_message(cid, "📤Here is your modified file ✅")

# ---------- RUN BOT ----------
print("✅ Bot is Running...")
bot.infinity_polling()