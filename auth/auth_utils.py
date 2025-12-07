from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_utils import get_current_user, decode_token, validate_user
from postgres.database import SessionDep


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def require_role(*allowed_roles: str):
    async def wrapper(
        session: SessionDep,
        token: str = Depends(oauth2_scheme)
    ):
        user = await get_current_user(token=token, session=session)

        if not bool(set([role.name for role in user.roles]) & set(allowed_roles)):
            raise HTTPException(
                403,
                "User is not eligible to access this method"
            )

        return user

    return wrapper