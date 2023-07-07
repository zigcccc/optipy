from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from optipy.auth import VerifyToken
from optipy.db.session import SessionLocal
from optipy.apps.users.models import User

from .exceptions import BadRequestFromRaisedException

token_auth_scheme = HTTPBearer()
token_verifier = VerifyToken()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_auth_token_sub(token: HTTPBearer = Depends(token_auth_scheme)) -> str:
    try:
        result = token_verifier.verify(token.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Token verification failed."
        )

    sub = result.get("sub", None)

    if sub == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return sub


def get_current_user(
    db: Session = Depends(get_db),
    sub: str = Depends(get_auth_token_sub),
) -> User:
    try:
        user = db.query(User).filter_by(sub=sub, is_active=True).first()

        if user is None:
            new_user = User(sub=sub)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return new_user

        return user

    except Exception as e:
        raise BadRequestFromRaisedException(e)
