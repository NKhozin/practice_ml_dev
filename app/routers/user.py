from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from database.functions import (add_access_token, add_user, authenticate_user,
                                change_user_balance, get_token_by_user_id,
                                get_user_by_username)
from dependencies import create_access_token, get_current_user
from models import User, UserOut

user_router = APIRouter()


@user_router.post("/signup", tags=["user"])
async def create_user_signup(user: User):
    """Регистрация"""
    db_user = get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    user = add_user(user.username, user.password)
    access_token = create_access_token(data={"sub": user.username})
    token = add_access_token(user.id, access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserOut(id=user.id, username=user.username, balance=user.balance),
    }


@user_router.post("/signin", tags=["user"])
async def login_for_access_token(user: User):
    """Авторизация"""
    user = authenticate_user(user.username, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = get_token_by_user_id(user.id)
    return {
        "access_token": token.access_token,
        "token_type": "bearer",
        "user": UserOut(id=user.id, username=user.username, balance=user.balance),
    }


@user_router.get("/change_balance/{amount}", tags=["user"])
async def change_balance(amount: int, current_user: Annotated[User, Depends(get_current_user)]):
    """Изменение баланса пользователя"""
    response = change_user_balance(current_user.username, amount)
    return {"success": "true", "current_user": current_user, "balance": response['balance']}


@user_router.get("/me", tags=["user"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Получения текущего пользователя"""
    return {"success": "true", "current_user": current_user}


@user_router.get("/balance", tags=["user"])
async def show_user_balance(current_user: Annotated[User, Depends(get_current_user)]):
    """Получение баланса текущего пользователя"""
    return {"success": "true", "current_user": current_user, "balance:": current_user.balance}
