from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import RegisterRequest, UserOut, TokenOut
from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
from app.core.exceptions import UnauthorizedError, BadRequestError
from app.core.config import get_settings, Settings
from app.db.database import get_db
from app.models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedError()
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError()
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError()
    
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError()
    
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user."""
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise BadRequestError("Email already registered")
    
    user = User(
        email=body.email,
        hashed_password=get_password_hash(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenOut)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenOut:
    """Login and get an access token."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError("Invalid credentials")
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenOut(
        access_token=token,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the current user profile."""
    return current_user
