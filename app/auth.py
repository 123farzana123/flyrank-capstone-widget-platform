import os
import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

load_dotenv()

SUPABASE_PROJECT_URL = os.environ["SUPABASE_PROJECT_URL"]
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()

_jwks = httpx.get(JWKS_URL).json()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract the user ID (sub claim) from the JWT in the Authorization header.

    Supabase signs tokens using ES256 (asymmetric key pair), so verification
    uses Supabase's PUBLIC key (fetched from their JWKS endpoint), not a
    shared secret. Raises HTTPException(401) if the token is missing,
    invalid, or expired.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            _jwks,
            algorithms=["ES256"],
            audience="authenticated",
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub claim")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")