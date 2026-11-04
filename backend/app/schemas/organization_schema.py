from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.email_normalization import normalize_email

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
RESERVED_SLUGS = frozenset({"www", "api", "admin", "app"})


class OrganizationCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=120)
    slug: str = Field(min_length=3, max_length=40, pattern=SLUG_PATTERN)
    admin_name: str = Field(min_length=3, max_length=120)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)

    @field_validator("slug")
    @classmethod
    def reject_reserved_slug(cls, slug: str) -> str:
        if slug in RESERVED_SLUGS:
            raise ValueError("Subdomínio reservado.")
        return slug

    @field_validator("admin_email")
    @classmethod
    def lowercase_admin_email(cls, email: str) -> str:
        return normalize_email(email)


class OrganizationUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=3, max_length=120)
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    status: str
    created_at: datetime


class PublicOrganizationResponse(BaseModel):
    name: str
    slug: str
    primary_color: str | None = None
    secondary_color: str | None = None
    logo_url: str | None = None
