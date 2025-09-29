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
TELEGRAM_BOT_TOKEN = "7380830860:AAGVLhA0T0N45ulztHiYZQy6wlNycjHPMno"
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

    with open(outpath,"w",encoding="utf-8") as f: f.write(loader)
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

# ------------------- Document handler -------------------
@bot.message_handler(content_types=['document'])
def handle_doc(msg):
    if not check_all_channels(msg.from_user.id):
        send_join_channels_msg(msg.chat.id)
        return
    doc=msg.document
    if not doc.file_name.lower().endswith(".py"):
        bot.reply_to(msg,"Kripya .py file bhejein.")
        return
    if doc.file_size > MAX_FILE_SIZE:
        bot.reply_to(msg,"File bahut badi hai (limit 30 MB).")
        return
    tmp_dir=tempfile.mkdtemp(prefix=f"enc_{msg.from_user.id}_")
    local_path=os.path.join(tmp_dir,doc.file_name)
    info=bot.get_file(doc.file_id)
    write_bytes(local_path,bot.download_file(info.file_path))
    USER_CTX[msg.from_user.id]={"file_path":local_path,"tmp_dir":tmp_dir,"orig_name":doc.file_name}

    buttons=[
        ("🅱️ Base64","base64"),("🌀 Gzip+Base64","gzip"),("📦 Zlib+Base64","zlib"),
        ("🔧 Raw Zlib","raw_zlib"),("📜 Marshal","marshal"),("🔒 XOR+Base64","xor"),
        ("🛡️ Bz2+Base64","bz2"),("🔑 Rot13+Base64","rot13"),("⚡ Hex+Base64","hex_b64"),
        ("🧬 LZMA+Base85","lzma85"),("🔐 ROT47+Hex","rot47hex"),("🧪 LZMA+Base85+Marshal","lzma_b85_marshal"),
        ("🧿 ROT47+BZ2+Base64","rot47_bz2_b64"),("⚡ XOR+LZMA+Base85","xor_lzma85"),("💥 UltraX (Triple Mix)","ultrax"),
        ("🌀 InfinityLock","infinitylock"),("🕳️ BlackBox Exec","blackbox_exec")
    ]
    cancel_btn=("❌ Cancel","cancel")
    markup=types.InlineKeyboardMarkup(row_width=2)
    for i in range(0,len(buttons),2):
        pair=buttons[i:i+2]
        markup.add(*(types.InlineKeyboardButton(text,callback_data=cb) for text,cb in pair))
    markup.add(types.InlineKeyboardButton(cancel_btn[0],callback_data=cancel_btn[1]))
    bot.reply_to(msg,"Choose encoding:",reply_markup=markup)

# ------------------- Callback handler -------------------
@bot.callback_query_handler(func=lambda c: True)
def process(call):
    uid = call.from_user.id

    # Broadcast only for admin
    if call.data == "broadcast":
        if uid != OWNER_ID:
            bot.answer_callback_query(call.id,"❌ Unauthorized")
            return
        bot.send_message(call.message.chat.id,"📢 Send your broadcast message now (it will go to all users).")
        OWNER_BROADCAST_MODE[OWNER_ID] = True
        return

    if uid not in USER_CTX:
        bot.answer_callback_query(call.id,"No pending file.")
        return

    ctx=USER_CTX[uid]
    infile=ctx["file_path"]
    tmp_dir=ctx["tmp_dir"]
    base=os.path.splitext(os.path.basename(ctx["orig_name"]))[0]
    out_name=_pain_name(base)+".py"
    out_path=os.path.join(tmp_dir,out_name)

    if call.data=="cancel":
        bot.edit_message_text("Cancelled.",call.message.chat.id,call.message.message_id)
        shutil.rmtree(tmp_dir,ignore_errors=True)
        USER_CTX.pop(uid,None)
        return

    try:
        spinner=["⏳","🔄","⌛"]
        msg=bot.send_message(call.message.chat.id,f"{spinner[0]} Encoding...")
        for s in spinner[1:]:
            time.sleep(0.5)
            bot.edit_message_text(f"{s} Encoding...",call.message.chat.id,msg.message_id)
        create_wrapper(infile,out_path,call.data)
        with open(out_path,"rb") as f:
            bot.send_document(call.message.chat.id,f,caption=f"{call.data} -> {out_name}")
        bot.edit_message_text(f"{call.data} operation done ✅",call.message.chat.id,msg.message_id)
    except Exception as e:
        logging.exception("error")
        bot.send_message(call.message.chat.id,f"Failed: {e}")
    finally:
        shutil.rmtree(tmp_dir,ignore_errors=True)
        USER_CTX.pop(uid,None)

# ------------------- Broadcast message handler -------------------
@bot.message_handler(content_types=["text"])
def broadcast_handler(message):
    if OWNER_BROADCAST_MODE.get(OWNER_ID):
        OWNER_BROADCAST_MODE[OWNER_ID] = False
        sent_count=0
        failed_count=0
        for uid in REGISTERED_USERS:
            if uid == OWNER_ID: continue
            try: bot.send_message(uid,message.text)
            except: failed_count+=1
            else: sent_count+=1
        bot.send_message(OWNER_ID,f"📢 Broadcast done ✅\nSent:{sent_count}\nFailed:{failed_count}")

# ------------------- Start bot -------------------
if __name__=="__main__":
    logging.info("Bot started ✅")
    bot.infinity_polling()