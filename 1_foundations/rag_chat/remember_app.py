from dotenv import load_dotenv
from openai import OpenAI
import os, requests, time
import gradio as gr

load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ORACLE_VM_URL = "http://158.180.52.220:8000"  # VM with Chroma API

def remember_fact(message, history):
    """Store a new fact with embedding in ChromaDB."""
    try:
        embedding = client.embeddings.create(
            input=message, model="text-embedding-3-small"
        ).data[0].embedding

        data = {
            "id": f"fact_{int(time.time())}",
            "fact": message,
            "embedding": embedding
        }

        resp = requests.post(f"{ORACLE_VM_URL}/remember", json=data)
        if resp.status_code == 200:
            return f"✅ Fact stored: {message}"
        else:
            return f"❌ Error storing fact: {resp.text}"
    except Exception as e:
        return f"⚠️ Error: {e}"

if __name__ == "__main__":
    gr.ChatInterface(
        remember_fact,
        type="messages",
        title="📝 Add Facts",
        description="Type a fact about yourself to store it in memory."
    ).launch()
