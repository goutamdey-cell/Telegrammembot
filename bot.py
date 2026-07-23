import json, os, asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==========================================
# 🔥 SIRF EK JAGAH CHANGE KARO (TOKEN) 🔥
# ==========================================
TOKEN = "8765162298:AAGXfpkgAw3bd_6ekig9XQSFW5gDCbYEkR4"  # ⬅️ YAHAN @BotFather se MILA NAYA TOKEN DAALO

# (NEECHE SAB KUCH MAIN NE SET KAR DIYA HAI, ISE MAT CHHEDO)
OWNER_ID = 7504827194

CHANNELS = [
    "-1002310611158",
    "-1002363675161",
    "-1003031914625",
    "-1002286595341",
    "-1003468908725",
    "-1003589730154",
    "-1003861000989",
    "-1003587390302",
    "-1003833989680",
    "-1003596567961",
    "-1003944523544"
]
# ==========================================

DB_FILE = "stats.json"

def load_data():
    if not os.path.exists(DB_FILE):
        d = {"blacklist": [], "total_removes": 0, "total_bans": 0, "logs": []}
        save_data(d); return d
    with open(DB_FILE, "r") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w") as f: json.dump(d, f, indent=4)

def add_log(msg):
    d = load_data()
    d["logs"].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    if len(d["logs"]) > 100: d["logs"] = d["logs"][-100:]
    save_data(d)

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Channels", callback_data="list"), InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("📜 Logs", callback_data="logs"), InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

async def get_title(bot, chat_id):
    try: return (await bot.get_chat(chat_id)).title or str(chat_id)
    except: return str(chat_id)

async def kick_user(bot, channel, user_id):
    try:
        await bot.ban_chat_member(channel, user_id)
        await bot.unban_chat_member(channel, user_id)
        return True, "Kicked"
    except Exception as e: return False, str(e)

async def check_user(bot, channel, user_id):
    try:
        return (await bot.get_chat_member(channel, user_id)).status not in [ChatMember.LEFT, ChatMember.KICKED]
    except: return False

# ---- COMMANDS ----
async def start(update, context):
    if update.effective_user.id != OWNER_ID: return await update.message.reply_text("❌ Unauthorized.")
    await update.message.reply_text("👋 Namaste! Menu use karo:", reply_markup=get_menu())

async def list_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    text = "📋 **Channels:**\n"
    for ch in CHANNELS:
        text += f"- {await get_title(context.bot, ch)} (`{ch}`)\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    d = load_data()
    await update.message.reply_text(f"📊 Removes: {d['total_removes']}\n⛔ Bans: {d['total_bans']}\n👥 Blacklist: {len(d['blacklist'])}")

async def logs_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    d = load_data()
    await update.message.reply_text("📜 Logs:\n" + "\n".join(d["logs"][-5:]) or "No logs")

async def info_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    if not context.args: return await update.message.reply_text("Usage: /info USER_ID")
    target = int(context.args[0])
    text = f"🔍 User {target}:\n"
    for ch in CHANNELS:
        status = await check_user(context.bot, ch, target)
        text += f"{'✅' if status else '❌'} {await get_title(context.bot, ch)}\n"
    await update.message.reply_text(text)

async def removeall_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    if not context.args: return await update.message.reply_text("Usage: /removeall USER_ID")
    target = int(context.args[0])
    d = load_data()
    if target in d["blacklist"]: return await update.message.reply_text(f"⛔ {target} blacklist me hai. Pehle /unban karo.")
    msg = await update.message.reply_text(f"⏳ {target} ko nikaal raha hoon...")

res = []
    for ch in CHANNELS:
        s, err = await kick_user(context.bot, ch, target)
        res.append(f"{'✅' if s else '❌'} {await get_title(context.bot, ch)}")
    d = load_data(); d["total_removes"] += 1; save_data(d)
    add_log(f"RemoveAll: {target}")
    await msg.edit_text("🚫 Complete!\n" + "\n".join(res))

async def ban_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    if not context.args: return await update.message.reply_text("Usage: /ban USER_ID")
    target = int(context.args[0])
    d = load_data()
    if target not in d["blacklist"]:
        d["blacklist"].append(target); d["total_bans"] += 1; save_data(d); add_log(f"Ban: {target}")
        await update.message.reply_text(f"✅ {target} blacklist me daal diya.")
    else:
        await update.message.reply_text(f"ℹ️ {target} already blacklist me hai.")

async def unban_cmd(update, context):
    if update.effective_user.id != OWNER_ID: return
    if not context.args: return await update.message.reply_text("Usage: /unban USER_ID")
    target = int(context.args[0])
    d = load_data()
    if target in d["blacklist"]:
        d["blacklist"].remove(target); save_data(d); add_log(f"Unban: {target}")
        await update.message.reply_text(f"✅ {target} blacklist se hata diya.")
    else:
        await update.message.reply_text(f"ℹ️ {target} blacklist me nahi tha.")

async def callback_handler(update, context):
    q = update.callback_query; await q.answer()
    if q.from_user.id != OWNER_ID: return await q.edit_message_text("❌ Unauthorized.")
    if q.data == "list":
        txt = "📋 Channels:\n" + "\n".join([f"- {await get_title(context.bot, ch)}" for ch in CHANNELS])
        await q.edit_message_text(txt, reply_markup=get_menu())
    elif q.data == "stats":
        d = load_data()
        await q.edit_message_text(f"📊 Removes: {d['total_removes']}\nBans: {d['total_bans']}", reply_markup=get_menu())
    elif q.data == "logs":
        d = load_data()
        await q.edit_message_text("📜 Logs:\n" + "\n".join(d["logs"][-5:]), reply_markup=get_menu())
    elif q.data == "help":
        await q.edit_message_text("/list\n/stats\n/logs\n/info ID\n/removeall ID\n/ban ID\n/unban ID", reply_markup=get_menu())

# ---- RUN ----
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(CommandHandler("stats", stats_cmd))
app.add_handler(CommandHandler("logs", logs_cmd))
app.add_handler(CommandHandler("info", info_cmd))
app.add_handler(CommandHandler("removeall", removeall_cmd))
app.add_handler(CommandHandler("ban", ban_cmd))
app.add_handler(CommandHandler("unban", unban_cmd))
app.add_handler(CallbackQueryHandler(callback_handler))

print("🚀 Bot chal raha hai! (Owner only)")
app.run_polling()
