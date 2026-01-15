from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.auth import verify_token

security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    user_id = verify_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
