#!/usr/bin/env python3
"""
Ultimate Hard Encoder Telegram Bot (Public Version)
- 20 encoding modes (17 normal + 3 ultra-hard runnable)
- Full encoding buttons
- No expiry, no owner-only restriction for encoding
- Broadcast button visible only to admin
"""

import os, tempfile, shutil, logging, base64, gzip, zlib, stat, marshal, bz2, codecs, binascii, lzma
import secrets, time
from telebot import TeleBot, types

# === Config ===
TELEGRAM_BOT_TOKEN = "7208934383:AAEvCS7ZN3KpoVt_wqgPhzAS3Uu26Q0H-fw"
OWNER_ID = 5840953778  # Admin for broadcast
MAX_FILE_SIZE = 30*1024*1024
REQUIRED_CHANNELS = ["@P4XPY","@P4INGOD"]

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
            if st not in ("member","administrator","creator"):
                return False
        except Exception: return False
    return True

def send_join_channels_msg(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for ch in REQUIRED_CHANNELS:
        btn = types.InlineKeyboardButton("🔗 JOIN", url=f"https://t.me/{ch.strip('@')}")
        markup.add(btn)
    bot.send_message(chat_id,"❌ Bot use karne ke liye pehle sabhi channels join karein.",reply_markup=markup)

def write_bytes(path,data):
    with open(path,"wb") as f: f.write(data)

# ------------------- Encoding wrapper -------------------
def create_wrapper(infile,outpath,mode):
    with open(infile,"r",encoding="utf-8",errors="replace") as f: src_text=f.read()
    src_bytes=src_text.encode("utf-8")

    # --- All encoding modes ---
    if mode=="base64":
        payload=base64.b64encode(src_bytes).decode()
        loader=f'import base64\nexec(compile(base64.b64decode("{payload}"),"{infile}","exec"))\n'
    elif mode=="gzip":
        payload=base64.b64encode(gzip.compress(src_bytes)).decode()
        loader=f'import base64,gzip\nexec(compile(gzip.decompress(base64.b64decode("{payload}")),"{infile}","exec"))\n'
    elif mode=="zlib":
        payload=base64.b64encode(zlib.compress(src_bytes)).decode()
        loader=f'import base64,zlib\nexec(compile(zlib.decompress(base64.b64decode("{payload}")),"{infile}","exec"))\n'
    elif mode=="raw_zlib":
        payload=zlib.compress(src_bytes)
        loader=f'import zlib,base64\nexec(compile(zlib.decompress({payload}),"{infile}","exec"))\n'
    elif mode=="marshal":
        payload=base64.b64encode(marshal.dumps(compile(src_text,infile,"exec"))).decode()
        loader=f'import marshal,base64\nexec(marshal.loads(base64.b64decode("{payload}")))\n'
    elif mode=="xor":
        key=secrets.token_bytes(16)
        encrypted=bytes([b^key[i%len(key)] for i,b in enumerate(src_bytes)])
        payload=base64.b64encode(encrypted).decode()
        loader=f"import base64\nkey={list(key)}\nenc=base64.b64decode('{payload}')\ndec=bytes([enc[i]^key[i%len(key)] for i in range(len(enc))])\nexec(compile(dec,'{infile}','exec'))\n"
    elif mode=="bz2":
        payload=base64.b64encode(bz2.compress(src_bytes)).decode()
        loader=f'import bz2,base64\nexec(compile(bz2.decompress(base64.b64decode("{payload}")),"{infile}","exec"))\n'
    elif mode=="rot13":
        payload=base64.b64encode(codecs.encode(src_text,"rot_13").encode()).decode()
        loader=f'import base64,codecs\nexec(compile(codecs.decode(base64.b64decode("{payload}").decode(),"rot_13"),"{infile}","exec"))\n'
    elif mode=="hex_b64":
        payload=base64.b64encode(binascii.hexlify(src_bytes)).decode()
        loader=f'import base64,binascii\nexec(compile(binascii.unhexlify(base64.b64decode("{payload}")),"{infile}","exec"))\n'
    elif mode=="lzma85":
        payload=base64.b85encode(lzma.compress(src_bytes)).decode()
        loader=f'import lzma,base64\nexec(compile(lzma.decompress(base64.b85decode("{payload}")),"{infile}","exec"))\n'
    elif mode=="rot47hex":
        def rot47(s): return ''.join(chr(33+((ord(c)-33+47)%94)) if 33<=ord(c)<=126 else c for c in s)
        payload=binascii.hexlify(rot47(src_text).encode()).decode()
        loader=f'import binascii\nenc=binascii.unhexlify("{payload}").decode()\n"".join(chr(33+((ord(c)-33+47)%94)) if 33<=ord(c)<=126 else c for c in enc)\n'
    elif mode=="lzma_b85_marshal":
        payload=base64.b85encode(lzma.compress(marshal.dumps(compile(src_text,infile,"exec")))).decode()
        loader=f'import lzma,base64,marshal\nexec(marshal.loads(lzma.decompress(base64.b85decode("{payload}"))))\n'
    elif mode=="rot47_bz2_b64":
        def rot47(s): return ''.join(chr(33+((ord(c)-33+47)%94)) if 33<=ord(c)<=126 else c for c in s)
        enc=bz2.compress(rot47(src_text).encode())
        payload=base64.b64encode(enc).decode()
        loader="import bz2,base64\n" + \
               f"data=bz2.decompress(base64.b64decode('{payload}')).decode()\n" + \
               "dec=''.join(chr(33+((ord(c)-33+47)%94)) if 33<=ord(c)<=126 else c for c in data)\n" + \
               f"exec(compile(dec,'{infile}','exec'))\n"
    elif mode=="xor_lzma85":
        key=secrets.token_bytes(32)
        encrypted=bytes([b^key[i%len(key)] for i,b in enumerate(src_bytes)])
        payload=base64.b85encode(lzma.compress(encrypted)).decode()
        loader=f"import lzma,base64\nkey={list(key)}\nenc=lzma.decompress(base64.b85decode('{payload}'))\ndec=bytes([enc[i]^key[i%len(key)] for i in range(len(enc))])\nexec(compile(dec,'{infile}','exec'))\n"
    elif mode=="ultrax":
        step1=zlib.compress(src_bytes)
        step2=bz2.compress(step1)
        payload=base64.b85encode(step2).decode()
        loader=f"import zlib,bz2,base64\nexec(compile(zlib.decompress(bz2.decompress(base64.b85decode('{payload}'))),'{infile}','exec'))\n"
    elif mode=="infinitylock":
        payload=base64.b64encode(src_bytes).decode()
        loader=f"import base64\ncode='{payload}'\nwhile True:\n exec(compile(base64.b64decode(code),'<locked>','exec'))\n"
    elif mode=="blackbox_exec":
        marsh=marshal.dumps(compile(src_text,infile,"exec"))
        packed=zlib.compress(bz2.compress(marsh))
        payload=base64.b85encode(packed).decode()
        loader="import base64,zlib,bz2,marshal\n" + \
               "a=''.join([chr(x) for x in [101,120,101,99]])\n" + \
               "b=''.join([chr(x) for x in [99,111,109,112,105,108,101]])\n" + \
               f"data=base64.b85decode('{payload}')\n" + \
               "m=zlib.decompress(bz2.decompress(data))\n" + \
               "code_obj=marshal.loads(m)\n" + \
               "globals().clear()\nlocals_map={}\n" + \
               "eval(b+'(code_obj,\"'+__file__+'\",\"exec\")',globals(),locals_map)\n" + \
               "eval(a+'(locals_map.get(\"__builtins__\",__builtins__))')\n" + \
               "exec(code_obj)\n"
    else: raise ValueError("Unknown mode")

    with open(outpath,"w",encoding="utf-8") as f:
        f.write("#𝐄𝐍𝐂𝐎𝐃𝐄 𝐁𝐘 𝐏𝐀𝐈𝐍\n")  # <<=== Yaha pehli line add ki
        f.write(loader)
    os.chmod(outpath,stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)

# ------------------- /start handler -------------------
@bot.message_handler(commands=['start'])
def welcome(msg):
    REGISTERED_USERS.add(msg.chat.id)
    markup = types.InlineKeyboardMarkup()

    # Admin gets broadcast button
    if msg.from_user.id == OWNER_ID:
        markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="broadcast"))

    bot.send_message(msg.chat.id,"👋 Welcome! Send a .py file to encode.", reply_markup=markup)

    # --- Owner ko notification bhejna (emoji + info ke sath) ---
    try:
        username = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.first_name
        lang = msg.from_user.language_code if msg.from_user.language_code else "Unknown"
        join_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        bot.send_message(
            OWNER_ID,
            f"🚀 Bot Started\n\n"
            f"👤 User: {username}\n"
            f"🆔 ID: `{msg.from_user.id}`\n"
            f"🌐 Lang: {lang}\n"
            f"📅 Time: {join_time}",
            parse_mode="Markdown"
        )
    except:
        pass

# ------------------- (baaki sab wahi hai) -------------------
# Document handler, callback handler, broadcast handler, etc. (unchanged)
# -----------------------------------------------------------

if __name__=="__main__":
    logging.info("Bot started ✅")
    bot.infinity_polling()