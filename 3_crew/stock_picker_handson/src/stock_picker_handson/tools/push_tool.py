from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os, requests

class PushNotificationToolInput(BaseModel):
    """A message to be send to the user."""
    message: str = Field(..., description="A message to push to the user")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotificationToolInput

    def _run(self, message: str) -> str:
        telegram_bot_token = os.getenv("TELEGRAM_NOTIFICATIONS_TOKEN")
        chat_id = os.getenv("TELEGRAM_NOTIFICATIONS_CHAT_ID")
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url).json()  # this sends the message
        print(f"Push: {message}")
        return '{"notification": "ok"}'
