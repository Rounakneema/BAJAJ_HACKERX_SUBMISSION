import uuid
import time
import asyncio
import re
from aiolimiter import AsyncLimiter
from typing import List, Dict, Tuple
from . import document_parser, clause_splitter, llm_service, vector_store_service
from ..config import TOP_K_RESULTS

rate_limiter = AsyncLimiter(15, 60)

async def answer_one_question(document_id: str, question: str, question_embedding: List[float]) -> str:
    """Asynchronously handles the logic for a single question."""
    async with rate_limiter:
        retrieved_clauses = vector_store_service.query_by_vector(document_id, question_embedding, TOP_K_RESULTS)
        if not retrieved_clauses:
            return "Information not found in the provided document context."
        
        # Build a context string that now includes the parent heading
        context = "\n---\n".join([f"Source (Under Heading '{c.get('heading', 'N/A')}', Clause {c.get('clause_ref', 'N/A')} on Page {c.get('page_number', 'N/A')}): {c.get('text', '')}" for c in retrieved_clauses])
        
        return await llm_service.generate_answer(context, question)

async def process_request(document_url: str, questions: List[str]) -> Dict[str, List[str]]:
    """Orchestrates the RAG pipeline with advanced context enrichment."""
    document_id = str(uuid.uuid4())
    
    try:
        pages = document_parser.parse_document_from_url(document_url)
        if not pages:
            return {"answers": ["Document is empty." for _ in questions]}

        # --- NEW: Context Enrichment Step ---
        chunks_with_metadata = []
        clause_pattern = re.compile(r"^\s*(\d+(\.\d+)*(\.\w)*)\s")
        # Regex to find major headings (assumes they are uppercase and on their own line)
        heading_pattern = re.compile(r"^\s*([A-Z\s,()&]+)\n")
        
        current_heading = "General"

        for page_num, page_text in pages:
            # Find and update the current heading for this page
            heading_match = heading_pattern.search(page_text)
            if heading_match:
                current_heading = heading_match.group(1).strip()

            page_chunks = clause_splitter.split_text(page_text)
            for chunk in page_chunks:
                match = clause_pattern.search(chunk)
                clause_ref = match.group(1).strip() if match else f"Page {page_num}"
                
                chunks_with_metadata.append({
                    "text": chunk,
                    "page_number": page_num,
                    "clause_ref": clause_ref,
                    "document_id": document_id,
                    "heading": current_heading # Attach the last seen heading
                })
        
        chunk_texts = [item["text"] for item in chunks_with_metadata]
        
        initial_count = vector_store_service.get_vector_count()
        chunk_embeddings = llm_service.get_embeddings(chunk_texts)
        question_embeddings = llm_service.get_embeddings(questions)
        
        vector_store_service.upsert_chunks(document_id, chunks_with_metadata, chunk_embeddings)
        
        # Intelligent wait for indexing
        target_count = initial_count + len(chunks_with_metadata)
        for _ in range(15):
            time.sleep(1)
            current_count = vector_store_service.get_vector_count()
            if current_count >= target_count:
                break
        
        tasks = [
            answer_one_question(document_id, q, q_embedding)
            for q, q_embedding in zip(questions, question_embeddings)
        ]
        answers = await asyncio.gather(*tasks)
        
        return {"answers": answers}
    
    finally:
        vector_store_service.delete_by_id(document_id)