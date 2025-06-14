from fastapi import APIRouter

api_router = APIRouter(prefix="/api")


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
