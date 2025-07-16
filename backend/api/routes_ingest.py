from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from typing import Optional
import uuid
from ..text_extractors import extract_youtube_transcript, extract_pdf_text
from ..ingestor import ingest_data

router = APIRouter()
jwt_bearer = JwtAccessBearer(secret_key="supersecret")
sessions = {}


@router.post("/ingest")
async def ingest_route(
    youtube_url: Optional[str] = Form(None),
    pdf: Optional[UploadFile] = File(None),
    document_name: str = Form(...),
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
):
    session_id = str(uuid.uuid4())
    text = ""
    doc_type = "youtube" if youtube_url else "pdf"
    username = credentials.subject[
        "username"
    ]  # or credentials.username, depending on your JWT payload
    if youtube_url:
        text = await extract_youtube_transcript(youtube_url)
    elif pdf:
        text = await extract_pdf_text(pdf)
    else:
        return {"error": "No input provided."}
    if (
        not text
        or text.startswith("Error")
        or "No captions" in text
        or "No text found" in text
    ):
        return {"error": text}
    # Pass all metadata to ingest_data
    sessions[session_id] = await ingest_data(
        text, username, session_id, doc_type, document_name
    )
    return {"status": "success", "session_id": session_id}
