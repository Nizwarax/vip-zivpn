import logging
import json
import os
import subprocess
import time
import datetime
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Paths
USER_DB = "/etc/zivpn/users.db.json"
CONFIG_FILE = "/etc/zivpn/config.json"
BOT_CONFIG = "/etc/zivpn/bot_config.sh"
DOMAIN_FILE = "/etc/zivpn/domain.conf"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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

def load_users():
    if not os.path.exists(USER_DB):
        return []
    try:
        with open(USER_DB, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=4)

def sync_config():
    users = load_users()
    passwords = [u['password'] for u in users]

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
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

    # daemon-reload is not needed for config changes
    subprocess.run(["systemctl", "restart", "zivpn.service"])

def get_domain():
    if os.path.exists(DOMAIN_FILE):
        with open(DOMAIN_FILE, 'r') as f:
            return f.read().strip()
    return subprocess.getoutput("curl -s ifconfig.me")

async def restricted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reload config to get latest ID
    global ADMIN_ID
    ADMIN_ID = get_config_value("CHAT_ID")

    if not ADMIN_ID:
        await update.message.reply_text("Admin CHAT_ID not set in configuration.")
        return False

    # Check if user ID matches
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_ID):
        await update.message.reply_text("⛔ Unauthorized Access!")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return
    await update.message.reply_text(
        "🤖 **ZIVPN Manager Bot**\n\n"
        "Available Commands:\n"
        "/generate <user> <pass> <days> - Create account\n"
        "/trial - Create 60min trial account\n"
        "/renew <user> <days> - Extend expiry (from now)\n"
        "/delete <user> - Delete account\n"
        "/check - List active accounts\n"
        "/status - Server resources info",
        parse_mode='Markdown'
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /generate <username> <password> <days>")
        return

    username = args[0]
    password = args[1]
    try:
        days = int(args[2])
    except ValueError:
        await update.message.reply_text("Days must be a number.")
        return

    users = load_users()
    if any(u['username'] == username for u in users):
        await update.message.reply_text(f"User `{username}` already exists.", parse_mode='Markdown')
        return

    expiry_timestamp = int(time.time()) + (days * 86400)
    users.append({
        "username": username,
        "password": password,
        "expiry_timestamp": expiry_timestamp
    })
    save_users(users)
    sync_config()

    domain = get_domain()
    expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d')

    msg = (
        "✅ **Account Created**\n"
        f"👤 User: `{username}`\n"
        f"🔑 Pass: `{password}`\n"
        f"📅 Exp: `{expiry_date}`\n"
        f"🌍 Host: `{domain}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return

    username = "trial" + ''.join(random.choices(string.digits, k=4))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    minutes = 60

    users = load_users()
    # Ensure unique username
    while any(u['username'] == username for u in users):
        username = "trial" + ''.join(random.choices(string.digits, k=4))

    expiry_timestamp = int(time.time()) + (minutes * 60)
    users.append({
        "username": username,
        "password": password,
        "expiry_timestamp": expiry_timestamp
    })
    save_users(users)
    sync_config()

    domain = get_domain()
    expiry_time = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%H:%M')

    msg = (
        "✅ **Trial Account Created**\n"
        f"👤 User: `{username}`\n"
        f"🔑 Pass: `{password}`\n"
        f"⏳ Exp: `{minutes} Min` ({expiry_time})\n"
        f"🌍 Host: `{domain}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def delete_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: /delete <username>")
        return

    username = args[0]
    users = load_users()
    initial_len = len(users)
    users = [u for u in users if u['username'] != username]

    if len(users) == initial_len:
        await update.message.reply_text(f"User `{username}` not found.", parse_mode='Markdown')
        return

    save_users(users)
    sync_config()
    await update.message.reply_text(f"🗑 User `{username}` deleted.", parse_mode='Markdown')

async def renew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /renew <username> <days>")
        return

    username = args[0]
    try:
        days = int(args[1])
    except ValueError:
        await update.message.reply_text("Days must be a number.")
        return

    users = load_users()
    found = False
    new_expiry = 0
    for u in users:
        if u['username'] == username:
            # Logic: Sets new expiry from NOW + duration (same as menu script)
            new_expiry = int(time.time()) + (days * 86400)
            u['expiry_timestamp'] = new_expiry

            # Remove legacy expiry_date field if exists
            if 'expiry_date' in u:
                del u['expiry_date']

            found = True
            break

    if not found:
        await update.message.reply_text(f"User `{username}` not found.", parse_mode='Markdown')
        return

    save_users(users)
    sync_config() # Apply changes immediately

    expiry_date = datetime.datetime.fromtimestamp(new_expiry).strftime('%Y-%m-%d')
    await update.message.reply_text(f"🔄 User `{username}` renewed until `{expiry_date}`.", parse_mode='Markdown')

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return
    users = load_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    msg = "📜 **User List**\n"
    now = int(time.time())
    count = 0
    for u in users:
        exp = u.get('expiry_timestamp', 0)
        days_left = (exp - now) // 86400
        status = "🟢" if days_left >= 0 else "🔴"

        # Calculate readable time left
        if days_left < 0:
            time_str = "Expired"
        elif days_left == 0:
            mins_left = (exp - now) // 60
            if mins_left > 60:
                time_str = f"{mins_left // 60}h"
            else:
                time_str = f"{mins_left}m"
        else:
            time_str = f"{days_left}d"

        msg += f"{status} `{u['username']}` ({time_str})\n"
        count += 1
        if count >= 40: # Telegram message limit protection
            await update.message.reply_text(msg, parse_mode='Markdown')
            msg = ""
            count = 0

    if msg:
        await update.message.reply_text(msg, parse_mode='Markdown')

async def status_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restricted(update, context): return

    # Get RAM
    ram = subprocess.getoutput("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'")
    # Get CPU
    cpu = subprocess.getoutput("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{print 100 - $1\"%\"}'")
    # Uptime
    uptime = subprocess.getoutput("uptime -p")

    msg = (
        "🖥 **Server Status**\n"
        f"🧠 RAM: `{ram}`\n"
        f"⚡ CPU: `{cpu}`\n"
        f"⏱ Uptime: `{uptime}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

def main():
    # Reload token just in case
    global TOKEN
    TOKEN = get_config_value("BOT_TOKEN")

    if not TOKEN:
        print("Error: BOT_TOKEN not found in /etc/zivpn/bot_config.sh")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("trial", trial))
    app.add_handler(CommandHandler("delete", delete_acc))
    app.add_handler(CommandHandler("renew", renew))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("status", status_server))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
