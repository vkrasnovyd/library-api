import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

from library_api.settings import TIME_ZONE

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SEND_MESSAGE_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}"
)


def send_telegram_notification(text):
    current_time = datetime.now(ZoneInfo(TIME_ZONE))
    current_time = current_time.strftime(format="%Y-%m-%d, %H:%M")
    text = f"{current_time}\n\n{text}"

    send_message_url = f"{SEND_MESSAGE_URL}&text={text}"
    requests.post(send_message_url)
