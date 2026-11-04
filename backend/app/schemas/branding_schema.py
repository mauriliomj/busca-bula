from pydantic import BaseModel, Field, field_validator

HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"


class BrandingColorsRequest(BaseModel):
    primary_color: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)
    secondary_color: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def lowercase_color(cls, color: str | None) -> str | None:
        return color.lower() if color else None


class BrandingResponse(BaseModel):
    primary_color: str | None = None
    secondary_color: str | None = None
    logo_url: str | None = None
