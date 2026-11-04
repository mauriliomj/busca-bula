from sqlalchemy.orm import Session

from app.core.logo_validation import LogoUpload, validate_logo
from app.exceptions.domain_exceptions import LogoNotFoundError
from app.models.tenant.branding import Branding
from app.repositories.branding_repository import BrandingRepository
from app.schemas.branding_schema import BrandingColorsRequest, BrandingResponse


class BrandingService:
    def __init__(self, tenant_session: Session, organization_slug: str) -> None:
        self.organization_slug = organization_slug
        self.branding_repository = BrandingRepository(tenant_session)

    def get_branding(self) -> BrandingResponse:
        return self.build_response(self.branding_repository.find_current())

    def update_colors(self, request: BrandingColorsRequest) -> BrandingResponse:
        branding = self.branding_repository.find_or_create_current()
        branding.primary_color = request.primary_color
        branding.secondary_color = request.secondary_color
        return self.build_response(self.branding_repository.save(branding))

    def replace_logo(self, upload: LogoUpload) -> BrandingResponse:
        validated_upload = validate_logo(upload)
        branding = self.branding_repository.find_or_create_current()
        branding.logo = validated_upload.content
        branding.logo_content_type = validated_upload.content_type
        return self.build_response(self.branding_repository.save(branding))

    def remove_logo(self) -> BrandingResponse:
        branding = self.branding_repository.find_or_create_current()
        branding.logo = None
        branding.logo_content_type = None
        return self.build_response(self.branding_repository.save(branding))

    def read_logo(self) -> LogoUpload:
        branding = self.branding_repository.find_current_with_logo()
        if branding is None or not branding.has_logo or branding.logo is None:
            raise LogoNotFoundError()
        return LogoUpload(branding.logo, branding.logo_content_type)

    def build_logo_url(self, branding: Branding) -> str:
        version = int(branding.updated_at.timestamp())
        return f"/api/organizations/{self.organization_slug}/logo?v={version}"

    def build_response(self, branding: Branding | None) -> BrandingResponse:
        if branding is None:
            return BrandingResponse()
        return BrandingResponse(
            primary_color=branding.primary_color,
            secondary_color=branding.secondary_color,
            logo_url=self.build_logo_url(branding) if branding.has_logo else None,
        )
