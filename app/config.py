import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# --- Hackathon Configuration ---
HACKRX_BEARER_TOKEN = "897c4085e488464964d46f0bfe6bfe3b84a30469dd9cbd2cc323cb487017852e"

# --- Pinecone Configuration ---
PINECONE_INDEX_NAME = "hackrx-reusable"
PINECONE_ENVIRONMENT = "us-east-1" # This might be used by the PodSpec
# NEW: Add these two variables required by ServerlessSpec
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"


# --- Gemini Model Configuration ---
GEMINI_EMBEDDING_MODEL = "models/text-embedding-004"
GEMINI_LLM_MODEL = "gemini-2.5-flash"

# --- Retrieval Configuration ---

TOP_K_RESULTS = 5
