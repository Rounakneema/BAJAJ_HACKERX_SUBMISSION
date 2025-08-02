from fastapi import FastAPI, Depends
from app.models.schemas import SubmissionRequest, SubmissionResponse
from app.services.query_handler import process_request
from app.auth import verify_token

app = FastAPI(
    title="HackRx Final Optimized RAG API",
    description="A reusable and high-performance solution for the HackRx hackathon.",
    version="5.0.0"
)

@app.post(
    "/api/v1/hackrx/run",
    response_model=SubmissionResponse,
    dependencies=[Depends(verify_token)],
)
async def run_submission(request: SubmissionRequest):
    """
    Handles a submission by calling the fully optimized, async query handler.
    """
    return await process_request(
        document_url=request.documents,
        questions=request.questions
    )

@app.get("/")
def health_check():
    return {"status": "ok", "version": "5.0.0"}