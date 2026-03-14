from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.auth.jwt_handler import verify_access_token

# This tells FastAPI: "to get a token, the user must call /auth/login"
# It also adds a lock icon on every protected route in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    This function is used as a dependency in every protected route.
    It reads the JWT token, finds the user in the database, and returns them.

    Usage in a route:
        current_user: User = Depends(get_current_user)
    """
    # Verify the token and get the payload (data inside the token)
    payload = verify_access_token(token)

    # Get user id from the payload
    user_id = int(payload.get("sub"))

    # Find the user in the database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def require_founder(current_user: User = Depends(get_current_user)) -> User:
    """
    Only allows founders to access the route.
    If an investor tries to access, they get 403 Forbidden.

    Usage in a route:
        current_user: User = Depends(require_founder)
    """
    if current_user.role != UserRole.founder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only founders can perform this action."
        )
    return current_user


def require_investor(current_user: User = Depends(get_current_user)) -> User:
    """
    Only allows investors to access the route.
    If a founder tries to access, they get 403 Forbidden.

    Usage in a route:
        current_user: User = Depends(require_investor)
    """
    if current_user.role != UserRole.investor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only investors can perform this action."
        )
    return current_user