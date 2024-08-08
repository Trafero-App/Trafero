from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from db_layer import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(plain_password):
    return pwd_context.hash(plain_password)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], secret_key, encoding_algorithm):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[encoding_algorithm])
    except InvalidTokenError:
        return None
    
    username: str | None = payload.get("sub")
    if username is None:
        return None
    user = db.get_account_info(username)
    if user is None:
        return None
    return user

async def authenticate_user(username: str, password: str):
    user = await db.get_account_info(username)
    if not user:
        return False
    if hash_password(password) != user["password_hash"]:
        return False
    return user

def create_access_token(token_data: dict, secret_key, encoding_algorithm):
    encoded_jwt = jwt.encode(token_data, secret_key, algorithm=encoding_algorithm)
    return encoded_jwt


