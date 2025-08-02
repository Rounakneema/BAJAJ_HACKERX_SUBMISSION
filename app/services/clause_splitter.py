from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

def split_text(text: str) -> List[str]:
    """
    Splits a long text into smaller, semantically meaningful chunks using the
    industry-standard RecursiveCharacterTextSplitter.
    """
    if not text:
        return []
    
    # This splitter is robust and works well for general documents.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150, # A good overlap helps maintain context between chunks
        length_function=len,
    )
    return text_splitter.split_text(text)