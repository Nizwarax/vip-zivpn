#!/bin/bash
# install_bot.sh

echo -e "\033[1;33mInstalling ZIVPN Bot...\033[0m"

# Define the python executable we want to use for the system service
PYTHON_EXEC="/usr/bin/python3"

# Install Python3 and pip if not present
if ! command -v $PYTHON_EXEC &> /dev/null; then
    echo "Installing Python3..."
    apt-get update
    apt-get install -y python3 python3-pip
fi

# Ensure pip is available for that python
if ! $PYTHON_EXEC -m pip --version &> /dev/null; then
     apt-get install -y python3-pip
fi

# Install python-telegram-bot
echo "Installing python-telegram-bot library for $PYTHON_EXEC..."
# Try installing with --break-system-packages (for newer distros like Debian 12/Ubuntu 24)
if ! $PYTHON_EXEC -m pip install python-telegram-bot --break-system-packages; then
    echo "Retrying without --break-system-packages..."
    $PYTHON_EXEC -m pip install python-telegram-bot
fi

# Copy bot script
echo "Copying bot script..."
cp zivpn_bot.py /usr/local/bin/zivpn_bot.py
chmod +x /usr/local/bin/zivpn_bot.py

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/zivpn-bot.service <<EOF
[Unit]
Description=ZIVPN Telegram Bot
After=network.target

[Service]
ExecStart=$PYTHON_EXEC /usr/local/bin/zivpn_bot.py
Restart=always
User=root
WorkingDirectory=/etc/zivpn
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload daemon and enable service
echo "Starting service..."
systemctl daemon-reload
systemctl enable zivpn-bot.service
systemctl restart zivpn-bot.service

echo -e "\033[1;32mZIVPN Bot installed and started!\033[0m"
echo -e "Make sure to configure BOT_TOKEN and CHAT_ID in /etc/zivpn/bot_config.sh"
echo -e "You can use option [9] in the zivpn menu to configure them."
