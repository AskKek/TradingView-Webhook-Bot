# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : handler.py              #
# ----------------------------------------------- #

import smtplib
import ssl
from email.mime.text import MIMEText
import requests

try:
    import tweepy
except ImportError:
    tweepy = None

try:
    from discord_webhook import DiscordEmbed, DiscordWebhook
except ImportError:
    DiscordEmbed = DiscordWebhook = None

try:
    from slack_webhook import Slack
except ImportError:
    Slack = None

import config


def format_telegram_message(data):
    """Format message for TradingView trading signals"""
    import re
    from datetime import datetime

    # Get the original message
    original_msg = data["msg"].encode("latin-1", "backslashreplace").decode("unicode_escape")

    # Try to parse trading information from the message
    # Pattern: "SYMBOL has moved DIRECTION by PERCENTAGE in TIMEFRAME"
    pattern = r"(\w+)\s+has\s+moved\s+(upward|downward)\s+by\s+([\d.]+%)\s+in\s+(\w+)"
    match = re.search(pattern, original_msg, re.IGNORECASE)

    if match:
        symbol = match.group(1)
        direction = match.group(2)
        percentage = match.group(3)
        timeframe = match.group(4)

        # Determine emoji and action based on direction
        if direction.lower() == "upward":
            emoji = "🟢"
            action = "📈 BULLISH SIGNAL"
            arrow = "⬆️"
        else:
            emoji = "🔴"
            action = "📉 BEARISH SIGNAL"
            arrow = "⬇️"

        # Format professional trading message
        formatted_msg = f"""🚨 *TRADINGVIEW ALERT* 🚨

{emoji} *{symbol}* {arrow}

{action}
━━━━━━━━━━━━━━━━━━━━
📊 *Move:* {percentage} {direction}
⏰ *Timeframe:* {timeframe}
🕒 *Time:* {datetime.now().strftime('%H:%M:%S UTC')}
━━━━━━━━━━━━━━━━━━━━

💡 _Automated signal from TradingView_"""
    else:
        # Fallback to enhanced formatting for non-standard messages
        timestamp = datetime.now().strftime('%H:%M:%S UTC')
        formatted_msg = f"""🚨 *TRADINGVIEW ALERT* 🚨

📢 {original_msg}

🕒 *Time:* {timestamp}
━━━━━━━━━━━━━━━━━━━━
💡 _Automated signal from TradingView_"""

    return formatted_msg

def send_alert(data):
    # Use formatted message for Telegram, original for others
    original_msg = data["msg"].encode("latin-1", "backslashreplace").decode("unicode_escape")
    if config.send_telegram_alerts:
        try:
            chat_id = data.get("telegram", config.channel)
            telegram_url = f"https://api.telegram.org/bot{config.tg_token}/sendMessage"
            # Use formatted message for Telegram
            formatted_msg = format_telegram_message(data)
            payload = {
                "chat_id": chat_id,
                "text": formatted_msg,
                "parse_mode": "MARKDOWN"
            }
            response = requests.post(telegram_url, json=payload)
            response.raise_for_status()
        except KeyError:
            telegram_url = f"https://api.telegram.org/bot{config.tg_token}/sendMessage"
            formatted_msg = format_telegram_message(data)
            payload = {
                "chat_id": config.channel,
                "text": formatted_msg,
                "parse_mode": "MARKDOWN"
            }
            response = requests.post(telegram_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print("[X] Telegram Error:\n>", e)

    if config.send_discord_alerts:
        if DiscordWebhook is None or DiscordEmbed is None:
            print("[X] Discord Error: discord-webhook not installed")
            return
        try:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + data["discord"]
            )
            embed = DiscordEmbed(title=original_msg)
            webhook.add_embed(embed)
            webhook.execute()
        except KeyError:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + config.discord_webhook
            )
            embed = DiscordEmbed(title=original_msg)
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            print("[X] Discord Error:\n>", e)

    if config.send_slack_alerts:
        if Slack is None:
            print("[X] Slack Error: slack-webhook not installed")
            return
        try:
            slack = Slack(url="https://hooks.slack.com/services/" + data["slack"])
            slack.post(text=original_msg)
        except KeyError:
            slack = Slack(
                url="https://hooks.slack.com/services/" + config.slack_webhook
            )
            slack.post(text=original_msg)
        except Exception as e:
            print("[X] Slack Error:\n>", e)

    if config.send_twitter_alerts:
        if tweepy is None:
            print("[X] Twitter Error: tweepy not installed")
            return
        tw_auth = tweepy.OAuthHandler(config.tw_ckey, config.tw_csecret)
        tw_auth.set_access_token(config.tw_atoken, config.tw_asecret)
        tw_api = tweepy.API(tw_auth)
        try:
            tw_api.update_status(
                status=original_msg.replace("*", "").replace("_", "").replace("`", "")
            )
        except Exception as e:
            print("[X] Twitter Error:\n>", e)

    if config.send_email_alerts:
        try:
            email_msg = MIMEText(
                original_msg.replace("*", "").replace("_", "").replace("`", "")
            )
            email_msg["Subject"] = config.email_subject
            email_msg["From"] = config.email_sender
            email_msg["To"] = config.email_sender
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                config.email_host, config.email_port, context=context
            ) as server:
                server.login(config.email_user, config.email_password)
                server.sendmail(
                    config.email_sender, config.email_receivers, email_msg.as_string()
                )
                server.quit()
        except Exception as e:
            print("[X] Email Error:\n>", e)
