from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.auth.jwt_handler import verify_access_token

# HTTPBearer shows a simple "Value" box in Swagger where you paste your token
# This is cleaner than OAuth2PasswordBearer for our use case
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    payload = verify_access_token(token)
    user_id = int(payload.get("sub"))

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def require_founder(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.founder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only founders can perform this action."
        )
    return current_user


def require_investor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.investor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only investors can perform this action."
        )
    return current_user