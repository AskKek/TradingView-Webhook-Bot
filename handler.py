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


def send_alert(data):
    msg = data["msg"].encode("latin-1", "backslashreplace").decode("unicode_escape")
    if config.send_telegram_alerts:
        try:
            chat_id = data.get("telegram", config.channel)
            telegram_url = f"https://api.telegram.org/bot{config.tg_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "MARKDOWN"
            }
            response = requests.post(telegram_url, json=payload)
            response.raise_for_status()
        except KeyError:
            telegram_url = f"https://api.telegram.org/bot{config.tg_token}/sendMessage"
            payload = {
                "chat_id": config.channel,
                "text": msg,
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
            embed = DiscordEmbed(title=msg)
            webhook.add_embed(embed)
            webhook.execute()
        except KeyError:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + config.discord_webhook
            )
            embed = DiscordEmbed(title=msg)
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
            slack.post(text=msg)
        except KeyError:
            slack = Slack(
                url="https://hooks.slack.com/services/" + config.slack_webhook
            )
            slack.post(text=msg)
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
                status=msg.replace("*", "").replace("_", "").replace("`", "")
            )
        except Exception as e:
            print("[X] Twitter Error:\n>", e)

    if config.send_email_alerts:
        try:
            email_msg = MIMEText(
                msg.replace("*", "").replace("_", "").replace("`", "")
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
