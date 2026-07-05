"""
Authentication router for user login, registration, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, Company
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest,
    UserRegister,
    UserResponse,
)
from app.services.audit import AuditService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return access/refresh tokens.
    
    - **username**: Email or username
    - **password**: User password
    """
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="login",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=UserResponse)
async def register(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **username**: Unique username
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    """
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create company if doesn't exist (for first user)
    company = None
    if user_data.company_name:
        company = db.query(Company).filter(Company.name == user_data.company_name).first()
        if not company:
            company = Company(name=user_data.company_name)
            db.add(company)
            db.flush()
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        company_id=company.id if company else None,
        role="user",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="register",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return UserResponse.model_validate(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(lambda: None),  # Will be replaced with actual auth
    db: Session = Depends(get_db),
):
    """
    Logout user (invalidate token on client side).
    
    Note: JWT tokens are stateless. Client should discard tokens.
    For production, consider implementing token blacklist with Redis.
    """
    # Log audit
    if current_user:
        AuditService.log_action(
            db=db,
            action="logout",
            entity_type="user",
            entity_id=current_user.id,
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
    
    return {"message": "Successfully logged out"}
