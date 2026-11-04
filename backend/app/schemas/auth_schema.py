from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.email_normalization import normalize_email


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, email: str) -> str:
        return normalize_email(email)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
