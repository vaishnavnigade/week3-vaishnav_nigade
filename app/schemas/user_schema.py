from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Request body used when creating a new customer account."""

    name: str
    email: EmailStr
    password: str
    mobile: str


class UserLogin(BaseModel):
    """Request body used when logging in."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response returned after successful registration."""

    email: EmailStr
    message: str


class TokenResponse(BaseModel):
    """Response returned after successful login."""

    access_token: str
    token_type: str = "bearer"
    email: EmailStr
    role:str
    message: str


class UserRead(BaseModel):
    """Safe user representation that never exposes the password."""

    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True