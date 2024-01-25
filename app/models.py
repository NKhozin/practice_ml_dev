from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: Optional[str] = None


class TokenData(BaseModel):
    username: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    balance: int
