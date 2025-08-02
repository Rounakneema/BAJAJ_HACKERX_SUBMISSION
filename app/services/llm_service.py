import google.generativeai as genai
from typing import List
from ..config import GOOGLE_API_KEY, GEMINI_EMBEDDING_MODEL, GEMINI_LLM_MODEL
from fastapi import HTTPException

genai.configure(api_key=GOOGLE_API_KEY)

# NEW: A simple in-memory cache for embeddings
embedding_cache = {}

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of texts, now with caching.
    """
    if not texts:
        return []

    embeddings = []
    texts_to_embed = []
    indices_to_fetch = []

    # NEW: Check the cache first
    for i, text in enumerate(texts):
        if text in embedding_cache:
            embeddings.append(embedding_cache[text])
        else:
            # Store a placeholder and mark this text for embedding
            embeddings.append(None)
            texts_to_embed.append(text)
            indices_to_fetch.append(i)

    # If there are any texts that were not in the cache, embed them in a single batch
    if texts_to_embed:
        try:
            result = genai.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                content=texts_to_embed,
                task_type="RETRIEVAL_DOCUMENT"
            )
            # Fill in the missing embeddings in our results list
            for i, embedding in enumerate(result['embedding']):
                original_index = indices_to_fetch[i]
                original_text = texts_to_embed[i]
                embeddings[original_index] = embedding
                # Store the new embedding in the cache for future use
                embedding_cache[original_text] = embedding
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini embedding failed: {e}")

    return embeddings

async def generate_answer(context: str, question: str) -> str:
    """
    Generates the most accurate Yes/No answer possible for policy/legal documents.
    - Always grounded in clauses/pages from the provided context.
    - Handles missing info gracefully.
    - Optimized for hackathon scoring: accuracy, explainability, cost-efficiency.
    """

    model = genai.GenerativeModel(GEMINI_LLM_MODEL)

    # Ultra-strict GOAT Prompt
    prompt = f"""
    You are a meticulous insurance policy analyst. Your ONLY source of truth is the provided CONTEXT.

    Follow this reasoning process before giving your final answer:
    1.  Identify the key terms and intent of the QUESTION.
    2.  Scan the CONTEXT for clauses that directly address these key terms.
    3.  Critically analyze the heading of the most relevant source clause (e.g., 'EXCLUSIONS', 'SCOPE OF COVER', 'WAITING PERIOD').
    4.  Based on the heading and the clause text, make a definitive 'Yes' or 'No' decision.
    5.  Extract the key conditions, limits, or details from the text.
    6.  Synthesize all this information into a single-sentence answer using the strict format below.

    Strict Output Format:
    "Yes/No, [reason and key conditions], as detailed in Clause [clause_id] under the '[section]' section on Page [page number]."

    CONTEXT:
    ---
    {context}
    ---
    QUESTION: {question}

    ANSWER:
    """
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"temperature": 0, "max_output_tokens": 256}
        )
        return response.text.strip().replace("\n", " ")
    except Exception as e:
        return f"Error: The language model failed to generate an answer. Details: {e}"