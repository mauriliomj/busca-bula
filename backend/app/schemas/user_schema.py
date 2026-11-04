from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.email_normalization import normalize_email

Gender = Literal["feminino", "masculino", "outro", "nao-informar"]

BrazilianState = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


class UserRegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=120)
    age: int = Field(ge=1, le=120)
    gender: Gender
    email: EmailStr
    phone: str = Field(min_length=8, max_length=20)
    address: str = Field(min_length=3, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: BrazilianState
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, email: str) -> str:
        return normalize_email(email)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    name: str
    email: str
    age: int | None
    gender: str | None
    phone: str | None
    address: str | None
    city: str | None
    state: str | None


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    age: int | None = Field(default=None, ge=1, le=120)
    gender: Gender | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=20)
    address: str | None = Field(default=None, min_length=3, max_length=200)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: BrazilianState | None = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, email: str) -> str:
        return normalize_email(email)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class AccountDeletionRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    name: str
    email: str
    city: str | None
    state: str | None
    created_at: datetime
