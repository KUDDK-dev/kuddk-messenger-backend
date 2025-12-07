import base64
import hashlib
from datetime import timedelta, timezone, datetime
from tokenize import Token
from typing import Union

import bcrypt
import jwt
import os

from fastapi import HTTPException
from jwt import InvalidTokenError
from sqlalchemy import select

from postgres.database import SessionDep
from postgres.models import UserModel
from schemas import TokenSchema


def create_access_token(data: dict, expiration_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expiration_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm="HS256")

    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError as e:
        return {"error": f"Invalid token: {str(e)}"}


async def login_for_access_token(username: str, password: str, session: SessionDep) -> Token:
    user = await validate_user(username=username, password=password, session=session)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=15)

    access_token = create_access_token(
        data={"username": user.username, "roles": [role.name for role in user.roles]},
        expiration_delta=access_token_expires
    )

    return TokenSchema(access_token=access_token)


async def validate_user(session: SessionDep, username: str, password: str = None) -> UserModel | None:
    result = await session.execute(select(UserModel).where(UserModel.username == username))
    user = result.scalar_one_or_none()

    if user:
        if password is None:
            return user

        if verify_password(password, user.password):
            return user

    return None


async def get_current_user(token: str, session: SessionDep):
    credentials_exception = HTTPException(
        status_code=401,
        detail="User is invalid!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)

        username: str = payload.get("username")
        expires_at: str = payload.get("exp")

        if username is None:
            print("username is none")
            raise credentials_exception

        if datetime.now(timezone.utc).timestamp() > int(expires_at):
            raise credentials_exception

    except InvalidTokenError as e:
        print(f"token invalid {e}")
        raise credentials_exception

    user = await validate_user(username=username, session=session)

    if user is None:
        raise credentials_exception
    return user

def hash_password(password: str) -> str:
    encoded_bytes = base64.b64encode(password.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        encoded = base64.b64encode(password.encode('utf-8')).decode('utf-8')
        return encoded == hashed_password
    except:
        return False