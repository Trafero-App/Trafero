from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from db_layer import db
from typing import Literal
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

JWT_ALGORITHM = os.getenv("jwt_algorithm")
AUTHENTICATION_SECRET_KEY = os.getenv("auth_secret_key")
ACCESS_TOKEN_VALIDITY_TIME_IN_MINUTES = int(os.getenv("access_token_validity_time_in_minutes"))

expired_token_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired token")
unauthorizzed_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def hash_password(plain_password):
    return pwd_context.hash(plain_password)


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

async def decode_token(token):
    try:
        payload = jwt.decode(token, AUTHENTICATION_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise expired_token_error
    except InvalidTokenError:
        raise InvalidTokenError
    return payload

async def get_current_user(payload):
    
    username: str | None = payload.get("sub")
    account_type: Literal["passenger", "vehicle"] | None = payload.get("type")

    if username is None or account_type is None: return None
    
    user = await db.get_account_info(username, account_type)
    if user is None:
        return None
    return user


async def check_authorization(token, allowed):
    payload = await decode_token(token)
    
    user = await get_current_user(payload)

    if user is None: raise unauthorizzed_error
    if not (allowed == "*" or user["type"] == allowed):
        raise unauthorizzed_error
    return user
        
async def check_authorization_passenger(token: Annotated[str, Depends(oauth2_scheme)]): return await check_authorization(token, "passenger")
async def check_authorization_vehicle(token: Annotated[str, Depends(oauth2_scheme)]): return await check_authorization(token, "vehicle")
async def check_authorization_all(token: Annotated[str, Depends(oauth2_scheme)]): return await check_authorization(token, "*")

authorize_passenger = Annotated[dict, Depends(check_authorization_passenger)]
authorize_vehicle = Annotated[dict, Depends(check_authorization_vehicle)]
authorize_all = Annotated[dict, Depends(check_authorization_all)]

async def get_user(username: str, password: str, account_type: Literal["passenger", "vehicle"]):
    user = await db.get_account_info(username, account_type)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

def create_access_token(token_data: dict):
    token_data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_VALIDITY_TIME_IN_MINUTES)
    encoded_jwt = jwt.encode(token_data, AUTHENTICATION_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


