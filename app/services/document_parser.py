import requests
import io
import fitz  # PyMuPDF
import docx
import email
from email.policy import default
from bs4 import BeautifulSoup
from fastapi import HTTPException
from urllib.parse import urlparse
from typing import List, Tuple # NEW: Import List and Tuple for type hinting

def parse_document_from_url(url: str) -> List[Tuple[int, str]]:
    """
    Downloads a document from a URL and extracts its text, returning a list of
    (page_number, page_text) tuples.
    """
    try:
        path = urlparse(url).path
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_stream = io.BytesIO(response.content)

        if path.lower().endswith(".pdf"):
            # PDF files have pages, so we can extract them one by one.
            docs_with_pages = []
            with fitz.open(stream=content_stream, filetype="pdf") as doc:
                for page_num, page in enumerate(doc):
                    docs_with_pages.append((page_num + 1, page.get_text()))
            return docs_with_pages
        
        elif path.lower().endswith(".docx"):
            # DOCX files do not have a fixed page structure; treat the whole document as page 1.
            doc = docx.Document(content_stream)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            return [(1, full_text)]
        
        elif path.lower().endswith(".eml"):
            # EML files do not have pages; treat the whole body as page 1.
            msg = email.message_from_bytes(response.content, policy=default)
            plain_text_body = ""
            html_body = ""

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        plain_text_body = part.get_payload(decode=True).decode()
                        break
                    elif content_type == "text/html":
                        html_body = part.get_payload(decode=True).decode()

            if plain_text_body:
                return [(1, plain_text_body)]
            elif html_body:
                soup = BeautifulSoup(html_body, "html.parser")
                return [(1, soup.get_text())]
            else:
                return [(1, "")] # Return with page 1 but empty content
                
        else:
            raise ValueError("Unsupported document format in URL path.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")