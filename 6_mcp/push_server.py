import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

load_dotenv(override=True)

telegram_token = os.getenv("TELEGRAM_NOTIFICATIONS_TOKEN")
chat_id = os.getenv("TELEGRAM_NOTIFICATIONS_CHAT_ID")


mcp = FastMCP("push_server")


class PushModelArgs(BaseModel):
    message: str = Field(description="A brief message to push")


@mcp.tool()
def push(args: PushModelArgs):
    """Send a push notification with this brief message"""
    print(f"Push: {args.message}")
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    response = requests.post(
        url=url,
        params={'chat_id': chat_id, 'text': f'{args.message}', 'parse_mode': 'Markdown'}
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
