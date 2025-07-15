from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes_auth import router as auth_router
from .api.routes_ingest import router as ingest_router
from .api.routes_chat import router as chat_router
from .config import BACKEND_HOST, BACKEND_PORT
import uvicorn

load_dotenv(override=True)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router)
    app.include_router(ingest_router)
    app.include_router(chat_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
