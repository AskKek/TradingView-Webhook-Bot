# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : config.py               #
# ----------------------------------------------- #

import os
from dotenv import load_dotenv

# Load .env file for local development only
# Vercel will use environment variables from dashboard
load_dotenv()

# TradingView Example Alert Message:
# {
# "key":"9T2q394M92", "telegram":"-1001298977502", "discord":"789842349670960670/BFeBBrCt-w2Z9RJ2wlH6TWUjM5bJuC29aJaJ5OQv9sE6zCKY_AlOxxFwRURkgEl852s3", "msg":"Long #{{ticker}} at `{{close}}`"
# }

sec_key = os.getenv("SEC_KEY", "")  # Can be anything. Has to match with "key" in your TradingView alert message

# Telegram Settings
send_telegram_alerts = os.getenv("SEND_TELEGRAM_ALERTS", "False").lower() == "true"
tg_token = os.getenv("TG_TOKEN", "")  # Bot token. Get it from @Botfather
channel = int(os.getenv("TG_CHANNEL", "0"))  # Channel ID (ex. -1001487568087)

# Discord Settings
send_discord_alerts = os.getenv("SEND_DISCORD_ALERTS", "False").lower() == "true"
discord_webhook = os.getenv("DISCORD_WEBHOOK", "")  # Discord Webhook URL (https://support.discordapp.com/hc/de/articles/228383668-Webhooks-verwenden)

# Slack Settings
send_slack_alerts = os.getenv("SEND_SLACK_ALERTS", "False").lower() == "true"
slack_webhook = os.getenv("SLACK_WEBHOOK", "")  # Slack Webhook URL (https://api.slack.com/messaging/webhooks)

# Twitter Settings
send_twitter_alerts = os.getenv("SEND_TWITTER_ALERTS", "False").lower() == "true"
tw_ckey = os.getenv("TW_CKEY", "")
tw_csecret = os.getenv("TW_CSECRET", "")
tw_atoken = os.getenv("TW_ATOKEN", "")
tw_asecret = os.getenv("TW_ASECRET", "")

# Email Settings
send_email_alerts = os.getenv("SEND_EMAIL_ALERTS", "False").lower() == "true"
email_sender = os.getenv("EMAIL_SENDER", "")  # Your email address
email_receivers = os.getenv("EMAIL_RECEIVERS", "").split(",") if os.getenv("EMAIL_RECEIVERS") else ["", ""]  # Comma-separated receivers
email_subject = os.getenv("EMAIL_SUBJECT", "Trade Alert!")

email_port = int(os.getenv("EMAIL_PORT", "465"))  # SMTP SSL Port (ex. 465)
email_host = os.getenv("EMAIL_HOST", "")  # SMTP host (ex. smtp.gmail.com)
email_user = os.getenv("EMAIL_USER", "")  # SMTP Login credentials
email_password = os.getenv("EMAIL_PASSWORD", "")  # SMTP Login credentials
