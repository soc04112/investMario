import os
import jwt
from fastapi import Request, HTTPException, status



SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_12345")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_current_user(request: Request):
    token = request.cookies.get("jwt")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# def get_current_user(request: Request):
#     return {
#         "sub": "test-user",
#         "email": "test@test.com"
#     }
