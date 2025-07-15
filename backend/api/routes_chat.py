from fastapi import APIRouter, Depends
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from ..models import ChatRequest
from ..retrievers import get_context, get_answer
from .routes_ingest import sessions

router = APIRouter()
jwt_bearer = JwtAccessBearer(secret_key="supersecret")


@router.post("/chat")
async def chat_route(
    request: ChatRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
):
    vectordb = sessions.get(request.session_id)
    if not vectordb:
        return {"answer": "Session not found. Please ingest a document first."}
    try:
        context = get_context(vectordb, request)
        answer = get_answer(context, request)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error generating answer: {str(e)}"}
