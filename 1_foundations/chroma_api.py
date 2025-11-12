import time
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for Hugging Face Space
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # optionally restrict to HF Space domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="/home/ubuntu/chromadb_data")
collection = chroma_client.get_or_create_collection("personal_facts")

# OpenAI client for embedding generation
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request model for storing facts
class Fact(BaseModel):
    fact: str  # client only sends the fact string

@app.get("/retrieve")
def retrieve(query: str, k: int = 3):
    """Generate embedding on server, then query ChromaDB."""
    try:
        embedding = openai_client.embeddings.create(
            input=query, model="text-embedding-3-small"
        ).data[0].embedding

        results = collection.query(query_embeddings=[embedding], n_results=k)
        docs = results["documents"][0] if results["documents"] else []
        return {"results": docs}
    except Exception as e:
        return {"error": str(e)}

@app.post("/remember")
def remember(fact: Fact):
    """Generate embedding on server and store it in ChromaDB."""
    try:
        embedding = openai_client.embeddings.create(
            input=fact.fact, model="text-embedding-3-small"
        ).data[0].embedding

        fact_id = f"fact_{int(time.time())}"
        collection.add(
            documents=[fact.fact],
            embeddings=[embedding],
            ids=[fact_id]
        )
        return {"status": "ok", "fact": fact.fact}
    except Exception as e:
        return {"status": "error", "error": str(e)}

