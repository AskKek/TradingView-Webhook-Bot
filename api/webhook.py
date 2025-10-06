# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : api/webhook.py          #
# ----------------------------------------------- #

import sys
import os

# Add parent directory to path so we can import handler and config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from handler import send_alert
import config
import time
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_timestamp():
    timestamp = time.strftime("%Y-%m-%d %X")
    return timestamp


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint to verify deployment"""
    return jsonify({
        'status': 'online',
        'service': 'TradingView Webhook Bot',
        'telegram_alerts': config.send_telegram_alerts,
        'discord_alerts': config.send_discord_alerts,
        'slack_alerts': config.send_slack_alerts,
        'twitter_alerts': config.send_twitter_alerts,
        'email_alerts': config.send_email_alerts
    }), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    whitelisted_ips = ['52.89.214.238', '34.212.75.30', '54.218.53.128', '52.32.178.7']
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Extract the first IP if X-Forwarded-For contains multiple IPs
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()

    if client_ip not in whitelisted_ips:
        print(f"[X] {get_timestamp()} Unauthorized IP: {client_ip}")
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        if request.method == "POST":
            data = request.get_json()
            if data["key"] == config.sec_key:
                print(get_timestamp(), "Alert Received & Sent!")
                send_alert(data)
                return jsonify({'message': 'Webhook received successfully'}), 200
            else:
                print("[X]", get_timestamp(), "Alert Received & Refused! (Wrong Key)")
                return jsonify({'message': 'Unauthorized'}), 401

    except Exception as e:
        print("[X]", get_timestamp(), "Error:\n>", e)
        return jsonify({'message': 'Error'}), 400


# Export app for Vercel - no custom handler needed
# Vercel will automatically detect and use the Flask app instance
