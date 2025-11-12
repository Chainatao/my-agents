#!/bin/bash

echo "🚨 Cleaning ChromaDB setup from Ubuntu server..."

# 1️⃣ Remove system packages installed for ChromaDB
sudo apt purge -y \
    python3-pip \
    python3-venv \
    python3-dotenv \
    firewalld \
    # Add any other packages you installed for ChromaDB

# 2️⃣ Remove automatically installed dependencies
sudo apt autoremove --purge -y

# 3️⃣ Clean APT cache
sudo apt clean

# 4️⃣ Remove Python packages globally installed via pip
pip3 uninstall -y chromadb fastapi uvicorn openai python-dotenv requests pypdf gradio

# 5️⃣ Remove Python virtual environments if any
rm -rf ~/venv_chromadb  # change if your venv folder has a different name

# 6️⃣ Remove ChromaDB data folders
rm -rf /home/ubuntu/chromadb_data
rm -rf /home/ubuntu/me

echo "✅ ChromaDB cleanup complete. Server is back to a clean state."
