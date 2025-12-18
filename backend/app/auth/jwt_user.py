import os
import jwt
from fastapi import Request, HTTPException, status



SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_12345")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_current_user(request: Request):
    return {
        "sub": "test-user",
        "email": "test@test.com"
    }
