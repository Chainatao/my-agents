from dotenv import load_dotenv 
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
import time

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

ORACLE_VM_URL = os.getenv("ORACLE_RAG_DB_IP")

def push(text):
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            }
        )
    except:
        pass

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

# Tool definitions
record_user_details_json = {
    "name": "record_user_details",
    "description": "Record user email/name/notes",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "name": {"type": "string"},
            "notes": {"type": "string"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Record unknown questions",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

class Me:

    def __init__(self):
        self.openai = client
        self.name = "Dmitrii Blokhin"
        self.mode = "basic"

        # Load LinkedIn PDF
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text

        # Load summary
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def retrieve_context(self, query, k=3):
        """Send query string to VM; server generates embedding and returns results."""
        print(f"Retrieving context for query: {query}")
        try:
            resp = requests.get(
                f"{ORACLE_VM_URL}/retrieve",
                params={"query": query, "k": k}  # now sending text instead of embedding
            )
            results = resp.json().get("results", [])
            print(results)
            return "\n".join(results)
        except Exception as e:
            print("Error retrieving context:", e)
            return ""

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def system_prompt_basic(self, retrieved_context=""):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
        particularly questions related to {self.name}'s career, background, skills and experience. \
        Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
        You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
        Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
        If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"

        if retrieved_context:
            system_prompt += f"## Retrieved Personal Knowledge:\n{retrieved_context}\n\n"

        system_prompt += f"With this context, chat with the user as {self.name}."
        return system_prompt
    
    
    def girlfriend_prompt(self, retrieved_context=""):
        system_prompt = f"You are acting as {self.name}. You are talking with {self.name}'s girlfriend, Maria José Llamas Caballero. Call her 'Bombon'.\
        Be cheerful. Remember that you are talking with your girlfriend, and that you call her 'Bombon'. "
        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"

        if retrieved_context:
            system_prompt += f"## Retrieved Personal Knowledge:\n{retrieved_context}\n\n"

        system_prompt += f"With this context, chat with the user as {self.name}."
        return system_prompt
    
    def brother_prompt(self, retrieved_context=""):
        system_prompt = f"You are acting as {self.name}. You are talking with {self.name}'s brother, Ilia Blokhin, or one of his friends. Mint is your nickname.\
        Ask a question, if it is {self.name}'s Brother or some of his friend. In case of a friend ask for his/her name. Be cheerful. Remember whom you are talking with."
        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"

        if retrieved_context:
            system_prompt += f"## Retrieved Personal Knowledge:\n{retrieved_context}\n\n"

        system_prompt += f"With this context, chat with the user as {self.name}."
        return system_prompt
    
    def system_prompt(self, retrieved_context="", ):
        if self.mode == "basic":
            return self.system_prompt_basic(retrieved_context)
        elif self.mode == "boyfriend":
            return self.girlfriend_prompt(retrieved_context)
        elif self.mode == "brother":
            return self.brother_prompt(retrieved_context)
            
    def chat(self, message, history):

        #Check whether user is speaking to girlfriend or brother
        if "amori" in message.lower():
            self.mode = "boyfriend"
        elif "mint" in message.lower():
            self.mode = "brother"

        retrieved = self.retrieve_context(message)

        messages = [{"role": "system", "content": self.system_prompt(retrieved)}] + history + [{"role": "user", "content": message}]
        print(messages)
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                msg = response.choices[0].message
                tool_calls = msg.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(msg)
                messages.extend(results)

            else:
                done = True
        return response.choices[0].message.content

    def generate_welcome(self):

        system_prompt = f"You are acting as {self.name}. Answer questions professionally and engagingly. "\
                        f"Use the retrieved personal context when available."

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"

        system_prompt += f"With this context, chat with the user as {self.name}."

        system_prompt += "Try to avoid talking about real estate whenever possible."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Please generate the welcome message in English with your first name and a call to talk."}
        ]
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content


# --- Chat app with LLM-picked welcome ---

def launch_chat():
    me = Me()
    #welcome_msg = me.generate_welcome()

    # Create the interface
    iface = gr.ChatInterface(
        fn=me.chat,  # your chat method
        # Create a Chatbot component with the welcome message
        type="messages",  # ensures OpenAI-style role/content dicts
        title="Hi, there! Hola! Привет!",
        # description=f"<div align='center'><h3>{welcome_msg}</h3></div>",
        #chatbot = gr.Chatbot(value=[{"role": "system", "content": welcome_msg}], type="messages", label="Talk to me!", placeholder="< type your message here >",),
    )
    iface.launch()
    
if __name__ == "__main__":
    launch_chat()