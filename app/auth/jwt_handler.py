from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
import os

# These values come from your .env file
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def create_access_token(data: dict) -> str:
    """
    Creates a JWT token.
    'data' is a dictionary — we pass in user id, email, and role.
    The token will expire after ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # jwt.encode() converts the dictionary into a signed token string
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str) -> dict:
    """
    Reads and verifies a JWT token.
    Returns the data inside the token (user id, email, role).
    Raises an error if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # jwt.decode() reads the token and returns the original dictionary
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user id from the token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return payload

    except JWTError:
        raise credentials_exception