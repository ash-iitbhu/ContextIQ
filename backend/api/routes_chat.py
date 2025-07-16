from fastapi import APIRouter, Depends
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from ..models import ChatRequest
from .routes_ingest import sessions
from ..services import ChatWorkflow, ChatManager

router = APIRouter()
jwt_bearer = JwtAccessBearer(secret_key="supersecret")

workflow = ChatWorkflow()
manager = ChatManager(workflow)


@router.post("/chat")
async def chat_route(
    request: ChatRequest, credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
):
    vectordb = sessions.get(request.session_id)
    if not vectordb:
        return {"answer": "Session not found. Please ingest a document first."}
    try:
        answer = manager.handle_user_input(
            request.session_id, vectordb, request.message
        )
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error generating answer: {str(e)}"}
