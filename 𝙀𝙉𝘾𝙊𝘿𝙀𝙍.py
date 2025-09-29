#!/usr/bin/env python3
"""
Ultimate Hard Encoder Telegram Bot (Railway Ready Version)
"""

import os, tempfile, shutil, logging, base64, gzip, zlib, stat, marshal, bz2, codecs, binascii, lzma
import secrets, time
from telebot import TeleBot, types

# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Bot token from env
OWNER_ID = int(os.getenv("OWNER_ID", "0"))            # Owner ID from env
MAX_FILE_SIZE = 30*1024*1024
REQUIRED_CHANNELS = ["@P4XPY", "@P4INGOD", "@M4R3ET", "@notAcTinve"]

logging.basicConfig(level=logging.INFO)
bot = TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

USER_CTX = {}
REGISTERED_USERS = set()
OWNER_BROADCAST_MODE = {}

# ------------------- Helpers -------------------
def _pain_name(base): return f"{base.strip()}_enc"

def check_all_channels(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            st = bot.get_chat_member(ch, user_id).status
            if st not in ("member", "administrator", "creator"):
                return False
        except Exception:
            return False
    return True

def send_join_channels_msg(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for ch in REQUIRED_CHANNELS:
        btn = types.InlineKeyboardButton("🔗 JOIN", url=f"https://t.me/{ch.strip('@')}")
        markup.add(btn)
    bot.send_message(chat_id, "❌ Bot use karne ke liye pehle sabhi channels join karein.", reply_markup=markup)

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

# ------------------- Encoding wrapper -------------------
def create_wrapper(infile, outpath, mode):
    with open(infile, "r", encoding="utf-8", errors="replace") as f:
        src_text = f.read()
    src_bytes = src_text.encode("utf-8")

    # TODO: Encoding modes paste from your original file here

# ------------------- /start handler -------------------
@bot.message_handler(commands=['start'])
def welcome(msg):
    REGISTERED_USERS.add(msg.chat.id)
    markup = types.InlineKeyboardMarkup()

    if msg.from_user.id == OWNER_ID:
        markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="broadcast"))

    bot.send_message(msg.chat.id, "👋 Welcome! Send a .py file to encode.", reply_markup=markup)

if __name__ == "__main__":
    logging.info("Bot started ✅")
    bot.infinity_polling()
