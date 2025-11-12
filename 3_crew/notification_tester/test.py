import os, requests
from dotenv import load_dotenv

load_dotenv()


def notify(msg):
    message = msg
    TOKEN = os.getenv("TELEGRAM_NOTIFICATIONS_TOKEN")
    chat_id = os.getenv("TELEGRAM_NOTIFICATIONS_CHAT_ID")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()  # this sends the message

notify('test')