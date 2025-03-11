from fastapi import FastAPI, APIRouter, Depends
from starlette.middleware.cors import CORSMiddleware

from api.deps import validate_access_token, validate_admin_access
from api.routes.admin.chat import admin_chat_router
from api.routes.admin.resource import admin_resource_router
from api.routes.auth import auth_router
from api.routes.chat import chat_router
from api.routes.system import system_router, system_non_authenticated_router
from api.routes.user import user_router


def include_authenticated_routes(_app: FastAPI) -> None:
    authenticated_router = APIRouter(dependencies=[Depends(validate_access_token)])
    authenticated_router.include_router(chat_router)
    authenticated_router.include_router(user_router)
    authenticated_router.include_router(system_router)
    _app.include_router(authenticated_router)


def include_non_authenticated_routes(_app: FastAPI) -> None:
    non_authenticated_router = APIRouter()
    non_authenticated_router.include_router(auth_router)
    non_authenticated_router.include_router(system_non_authenticated_router)
    _app.include_router(non_authenticated_router)


def include_admin_routes(_app: FastAPI) -> None:
    admin_router = APIRouter(
        prefix="/admin", dependencies=[Depends(validate_admin_access)]
    )
    admin_router.include_router(admin_chat_router)
    admin_router.include_router(admin_resource_router)
    _app.include_router(admin_router)


def create_app() -> FastAPI:
    _app = FastAPI(root_path="/api")
    include_authenticated_routes(_app)
    include_non_authenticated_routes(_app)
    include_admin_routes(_app)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this to your needs
        allow_credentials=True,
        allow_methods=["POST", "GET", "DELETE", "OPTIONS"],
        allow_headers=["Authorization"],
    )
    return _app


app = create_app()
