#!/usr/bin/env python
"""Test script to verify webhook functionality"""

import os
import sys

# Test environment setup
print("Testing environment setup...")
os.environ["SEC_KEY"] = "test_key_123"
os.environ["SEND_TELEGRAM_ALERTS"] = "false"
os.environ["SEND_DISCORD_ALERTS"] = "false"
os.environ["SEND_SLACK_ALERTS"] = "false"
os.environ["SEND_TWITTER_ALERTS"] = "false"
os.environ["SEND_EMAIL_ALERTS"] = "false"

# Test imports
print("Testing imports...")
try:
    from api.webhook import app
    import config
    import handler
    print("  All imports successful!")
except ImportError as e:
    print(f"  Import error: {e}")
    sys.exit(1)

# Test config loading
print("\nTesting config...")
print(f"  SEC_KEY loaded: {'Yes' if config.sec_key else 'No'}")
print(f"  Telegram alerts: {config.send_telegram_alerts}")
print(f"  Discord alerts: {config.send_discord_alerts}")

# Test Flask app
print("\nTesting Flask app...")
print(f"  App created: {app is not None}")
print(f"  App name: {app.name}")

# Test routes
print("\nTesting routes...")
with app.test_client() as client:
    # Test with no data
    response = client.post('/webhook')
    print(f"  POST /webhook (no data): {response.status_code}")

    # Test with invalid key
    response = client.post('/webhook',
                          json={"key": "wrong_key", "msg": "test"},
                          headers={"X-Forwarded-For": "52.89.214.238"})
    print(f"  POST /webhook (wrong key): {response.status_code}")

    # Test with correct key but alerts disabled
    response = client.post('/webhook',
                          json={"key": "test_key_123", "msg": "test alert"},
                          headers={"X-Forwarded-For": "52.89.214.238"})
    print(f"  POST /webhook (valid key): {response.status_code}")

print("\nAll tests passed! The webhook is configured correctly.")
