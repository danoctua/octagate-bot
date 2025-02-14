from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routes.auth import auth_router
from api.routes.chat import chat_router
from api.routes.user import user_router


def create_app() -> FastAPI:
    _app = FastAPI(root_path="/api")
    _app.include_router(user_router)
    _app.include_router(auth_router)
    _app.include_router(chat_router)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this to your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return _app


app = create_app()
