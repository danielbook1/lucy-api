from fastapi import APIRouter
from .client_router import client_router
from .project_router import project_router
from .task_router import task_router

api_router = APIRouter(prefix="/api")
api_router.include_router(client_router)
api_router.include_router(project_router)
api_router.include_router(task_router)


@api_router.get("/")
def root():
    return {
        "message": "Welcome to the API!",
        "endpoints": {
            "client": "/api/client/",
            "project": "/api/project/",
            "task": "/api/task/",
        },
    }
