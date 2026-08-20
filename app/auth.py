import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# load the secret from environment
load_dotenv()

SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

#the security scheme
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract the user ID (sub claim) from the JWT in the Authorization header.

    Raises HTTPException(401) if the token is missing, invalid, or expired.
    """
    token = credentials.credentials # the raw JWT string, extracted from "Bearer <token>"
    try:
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            audience="authenticated")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub claim")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")