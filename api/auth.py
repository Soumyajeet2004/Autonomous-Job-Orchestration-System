from jose import jwt, JWTError
from api.config import JWT_SECRET

SECRET_KEY = JWT_SECRET
ALGORITHM = "HS256"

def create_token(user_id: str):
    return jwt.encode({"sub": user_id}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
