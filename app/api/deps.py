from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.services.auth import AuthService
from app.schemas.user import UserResponse
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_auth_service() -> AuthService:
    from app.main import app  # Local import to avoid circular dependency
    return AuthService(app.mongodb)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError()
    except JWTError:
        raise AuthenticationError()
    
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise AuthenticationError()
    
    return UserResponse(**user)