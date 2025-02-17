import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.routes.auth import auth_router
from api.routes.chat import chat_router
from api.routes.system import system_router
from api.routes.user import user_router


def create_app() -> FastAPI:
    _app = FastAPI(root_path="/api")
    _app.include_router(user_router)
    _app.include_router(auth_router)
    _app.include_router(chat_router)
    _app.include_router(system_router)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this to your needs
        allow_credentials=True,
        allow_methods=["POST", "GET", "DELETE", "OPTIONS"],
        allow_headers=["Authorization"],
    )
    return _app


app = create_app()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(
        f"Validation error: {exc.errors()} on request: {request.url} with body: {await request.body()}"
    )
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )
