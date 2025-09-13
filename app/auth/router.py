from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import UserRead, UserCreate, Token
from app.auth.services import create_user, login_user, get_current_user
from app.auth.models import User
from app.database import get_db
from app.config import JWT_EXP

router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_in)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    token = await login_user(db, form_data)

    response = JSONResponse(content={"message": "Logged in"})
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="strict",  # "lax" or "strict" depending on your needs
        max_age=JWT_EXP,
        secure=False,  # True in production with HTTPS
    )
    return response


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
