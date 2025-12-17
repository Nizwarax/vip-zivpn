import logging
import json
import os
import subprocess
import time
import datetime
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# Paths
USER_DB = "/etc/zivpn/users.db.json"
CONFIG_FILE = "/etc/zivpn/config.json"
BOT_CONFIG = "/etc/zivpn/bot_config.sh"
DOMAIN_FILE = "/etc/zivpn/domain.conf"
RESELLER_DB = "/etc/zivpn/resellers.json"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Conversation States
(
    SELECTING_ACTION,
    GEN_USER, GEN_PASS, GEN_DAYS,
    RENEW_USER, RENEW_DAYS,
    DEL_USER,
    ADD_RESELLER,
    DEL_RESELLER
) = range(9)

# --- Configuration & Helpers ---

def get_config_value(key):
    if not os.path.exists(BOT_CONFIG):
        return None
    with open(BOT_CONFIG, 'r') as f:
        for line in f:
            if line.startswith(key + "="):
                val = line.split("=", 1)[1].strip()
                return val.strip("'").strip('"')
    return None

TOKEN = get_config_value("BOT_TOKEN")
ADMIN_ID = get_config_value("CHAT_ID")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_resellers():
    return load_json(RESELLER_DB)

def save_resellers(data):
    save_json(RESELLER_DB, data)

def sync_config():
    users = load_json(USER_DB)
    passwords = [u['password'] for u in users]

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except:
            config = {}
    else:
        config = {}

    if 'auth' not in config: config['auth'] = {}
    config['auth']['config'] = passwords
    config['config'] = passwords

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

    subprocess.run(["systemctl", "restart", "zivpn.service"])

def get_public_ip():
    return subprocess.getoutput("curl -s ifconfig.me")

def get_domain():
    if os.path.exists(DOMAIN_FILE):
        with open(DOMAIN_FILE, 'r') as f:
            domain = f.read().strip()
            if domain: return domain
    return get_public_ip()

# --- Access Control ---

def get_admin_id():
    # Reload from config in case it changes
    return get_config_value("CHAT_ID")

def is_admin(user_id):
    admin_id = get_admin_id()
    return str(user_id) == str(admin_id)

def is_authorized(user_id):
    if is_admin(user_id):
        return True
    resellers = load_resellers()
    return str(user_id) in [str(r) for r in resellers]

async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.effective_message.reply_text("⛔ Unauthorized Access!")
        return False
    return True

# --- Menus ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context): return

    user_id = update.effective_user.id
    text = "🤖 **ZIVPN Control Panel**\nSelect an action below:"

    buttons = [
        [
            InlineKeyboardButton("➕ Generate SSH", callback_data='menu_generate'),
            InlineKeyboardButton("⏳ Trial Account", callback_data='menu_trial')
        ],
        [
            InlineKeyboardButton("🔄 Renew Account", callback_data='menu_renew'),
            InlineKeyboardButton("🗑 Delete Account", callback_data='menu_delete')
        ],
        [
            InlineKeyboardButton("📊 Check Users", callback_data='menu_check'),
            InlineKeyboardButton("🖥 Server Status", callback_data='menu_status')
        ]
    ]

    # Add Admin Only Buttons
    if is_admin(user_id):
        buttons.append([
            InlineKeyboardButton("👥 Manage Resellers", callback_data='menu_resellers')
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    return SELECTING_ACTION

async def reseller_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.message.reply_text("⛔ Admin only area.")
        return SELECTING_ACTION

    text = "👥 **Reseller Management**"
    buttons = [
        [InlineKeyboardButton("➕ Add Reseller", callback_data='reseller_add')],
        [InlineKeyboardButton("➖ Delete Reseller", callback_data='reseller_del')],
        [InlineKeyboardButton("📜 List Resellers", callback_data='reseller_list')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_back')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
    return SELECTING_ACTION

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)

# --- Action Handlers (Status & Trial & List) ---

async def action_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = "trial" + ''.join(random.choices(string.digits, k=4))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    minutes = 60

    users = load_json(USER_DB)
    while any(u['username'] == username for u in users):
        username = "trial" + ''.join(random.choices(string.digits, k=4))

    expiry_timestamp = int(time.time()) + (minutes * 60)
    users.append({
        "username": username,
        "password": password,
        "expiry_timestamp": expiry_timestamp
    })
    save_json(USER_DB, users)
    sync_config()

    domain = get_domain()
    public_ip = get_public_ip()
    expiry_time = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%d-%m-%Y %H:%M')

    msg = (
        "────────────────────\n"
        "    ☘ NEW TRIAL ACCOUNT ☘\n"
        "────────────────────\n"
        f"User      : `{username}`\n"
        f"Password  : `{password}`\n"
        f"HOST      : `{domain}`\n"
        f"IP VPS    : `{public_ip}`\n"
        f"EXP       : `{expiry_time}` / `{minutes}` MENIT\n"
        "────────────────────\n"
        "Note: Auto notif from your script..."
    )
    await query.edit_message_text(msg, parse_mode='Markdown')

    # Show menu again after short delay or simple back button?
    # Let's add a button to go back
    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='menu_back')]]
    await query.message.reply_text("Done.", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

async def action_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ram = subprocess.getoutput("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'")
    cpu = subprocess.getoutput("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{print 100 - $1\"%\"}'")
    uptime = subprocess.getoutput("uptime -p")

    msg = (
        "🖥 **Server Status**\n"
        f"🧠 RAM: `{ram}`\n"
        f"⚡ CPU: `{cpu}`\n"
        f"⏱ Uptime: `{uptime}`"
    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_back')]]
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

async def action_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    users = load_json(USER_DB)
    if not users:
        msg = "No users found."
    else:
        msg = "📜 **User List**\n"
        now = int(time.time())
        for u in users:
            exp = u.get('expiry_timestamp', 0)
            days_left = (exp - now) // 86400
            status = "🟢" if days_left >= 0 else "🔴"

            if days_left < 0:
                time_str = "Expired"
            elif days_left == 0:
                mins_left = (exp - now) // 60
                time_str = f"{mins_left}m"
            else:
                time_str = f"{days_left}d"

            msg += f"{status} `{u['username']}` ({time_str})\n"

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_back')]]
    # Split message if too long? For now assume it fits or simple split
    if len(msg) > 4000: msg = msg[:4000] + "..."
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

async def action_list_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    resellers = load_resellers()
    if not resellers:
        msg = "No resellers found."
    else:
        msg = "👥 **Reseller List**\n"
        for r in resellers:
            msg += f"🆔 `{r}`\n"

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_resellers')]]
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

# --- Generate Flow ---

async def start_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📝 **New Account**\nMasukkan Username:")
    return GEN_USER

async def gen_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    users = load_json(USER_DB)
    if any(u['username'] == username for u in users):
        await update.message.reply_text("❌ Username already exists. Try another:")
        return GEN_USER

    context.user_data['gen_username'] = username
    await update.message.reply_text("🔑 Masukkan Password:")
    return GEN_PASS

async def gen_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gen_password'] = update.message.text.strip()
    await update.message.reply_text("📅 Masukkan Durasi (hari):")
    return GEN_DAYS

async def gen_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Durasi harus angka. Masukkan Durasi (hari):")
        return GEN_DAYS

    username = context.user_data['gen_username']
    password = context.user_data['gen_password']

    users = load_json(USER_DB)
    expiry_timestamp = int(time.time()) + (days * 86400)
    users.append({
        "username": username,
        "password": password,
        "expiry_timestamp": expiry_timestamp
    })
    save_json(USER_DB, users)
    sync_config()

    domain = get_domain()
    public_ip = get_public_ip()
    expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%d-%m-%Y')

    msg = (
        "────────────────────\n"
        "    ☘ NEW ACCOUNT DETAIL ☘\n"
        "────────────────────\n"
        f"User      : `{username}`\n"
        f"Password  : `{password}`\n"
        f"HOST      : `{domain}`\n"
        f"IP VPS    : `{public_ip}`\n"
        f"EXP       : `{expiry_date}` / `{days}` HARI\n"
        "────────────────────\n"
        "Note: Auto notif from your script..."
    )

    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='menu_back')]]
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

# --- Renew Flow ---

async def start_renew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🔄 **Renew Account**\nMasukkan Username yang akan diperpanjang:")
    return RENEW_USER

async def renew_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    users = load_json(USER_DB)
    if not any(u['username'] == username for u in users):
        await update.message.reply_text("❌ Username tidak ditemukan. Masukkan Username lagi:")
        return RENEW_USER

    context.user_data['renew_username'] = username
    await update.message.reply_text("📅 Masukkan durasi tambahan (hari):")
    return RENEW_DAYS

async def renew_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Durasi harus angka. Masukkan durasi (hari):")
        return RENEW_DAYS

    username = context.user_data['renew_username']
    users = load_json(USER_DB)

    new_expiry = 0
    for u in users:
        if u['username'] == username:
            # Menu script logic: reset from NOW
            new_expiry = int(time.time()) + (days * 86400)
            u['expiry_timestamp'] = new_expiry
            if 'expiry_date' in u: del u['expiry_date']
            break

    save_json(USER_DB, users)
    sync_config()

    expiry_date = datetime.datetime.fromtimestamp(new_expiry).strftime('%d-%m-%Y')
    msg = f"✅ User `{username}` berhasil diperpanjang sampai `{expiry_date}`."

    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='menu_back')]]
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

# --- Delete Flow ---

async def start_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🗑 **Delete Account**\nMasukkan Username yang akan dihapus:")
    return DEL_USER

async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    users = load_json(USER_DB)

    found = False
    new_users = []
    for u in users:
        if u['username'] == username:
            found = True
        else:
            new_users.append(u)

    if not found:
        await update.message.reply_text("❌ Username tidak ditemukan. Batalkan? Ketik /cancel atau coba lagi:")
        return DEL_USER

    save_json(USER_DB, new_users)
    sync_config()

    msg = f"✅ User `{username}` berhasil dihapus."
    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='menu_back')]]
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

# --- Add Reseller Flow ---

async def start_add_reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("➕ **Add Reseller**\nMasukkan Telegram ID (angka):")
    return ADD_RESELLER

async def add_reseller_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reseller_id = update.message.text.strip()
    if not reseller_id.isdigit():
         await update.message.reply_text("❌ ID harus angka. Coba lagi:")
         return ADD_RESELLER

    resellers = load_resellers()
    if reseller_id in resellers:
        await update.message.reply_text("⚠️ ID ini sudah menjadi reseller.")
    else:
        resellers.append(reseller_id)
        save_resellers(resellers)
        await update.message.reply_text(f"✅ Reseller ID `{reseller_id}` ditambahkan.", parse_mode='Markdown')

    keyboard = [[InlineKeyboardButton("🔙 Reseller Menu", callback_data='menu_resellers')]]
    await update.message.reply_text("Kembali ke menu:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

# --- Delete Reseller Flow ---

async def start_del_reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("➖ **Delete Reseller**\nMasukkan Telegram ID yang akan dihapus:")
    return DEL_RESELLER

async def del_reseller_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reseller_id = update.message.text.strip()
    resellers = load_resellers()

    if reseller_id not in resellers:
        await update.message.reply_text("❌ ID tidak ditemukan di daftar reseller.")
    else:
        resellers.remove(reseller_id)
        save_resellers(resellers)
        await update.message.reply_text(f"✅ Reseller ID `{reseller_id}` dihapus.", parse_mode='Markdown')

    keyboard = [[InlineKeyboardButton("🔙 Reseller Menu", callback_data='menu_resellers')]]
    await update.message.reply_text("Kembali ke menu:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Action Cancelled.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data='menu_back')]]))
    return SELECTING_ACTION

# --- Main Setup ---

def main():
    # Reload token just in case
    global TOKEN
    TOKEN = get_config_value("BOT_TOKEN")

    if not TOKEN:
        print("Error: BOT_TOKEN not found in /etc/zivpn/bot_config.sh")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", start),
            CallbackQueryHandler(back_to_main, pattern='^menu_back$')
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(start_gen, pattern='^menu_generate$'),
                CallbackQueryHandler(action_trial, pattern='^menu_trial$'),
                CallbackQueryHandler(start_renew, pattern='^menu_renew$'),
                CallbackQueryHandler(start_del, pattern='^menu_delete$'),
                CallbackQueryHandler(action_check, pattern='^menu_check$'),
                CallbackQueryHandler(action_status, pattern='^menu_status$'),

                # Reseller Menu Navigation
                CallbackQueryHandler(reseller_menu, pattern='^menu_resellers$'),
                CallbackQueryHandler(start_add_reseller, pattern='^reseller_add$'),
                CallbackQueryHandler(start_del_reseller, pattern='^reseller_del$'),
                CallbackQueryHandler(action_list_resellers, pattern='^reseller_list$'),

                # Re-entry
                CallbackQueryHandler(back_to_main, pattern='^menu_back$')
            ],
            GEN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gen_user)],
            GEN_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gen_pass)],
            GEN_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gen_days)],

            RENEW_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, renew_user)],
            RENEW_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, renew_days)],

            DEL_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_user)],

            ADD_RESELLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reseller_input)],
            DEL_RESELLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_reseller_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
