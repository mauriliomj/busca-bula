from fastapi import APIRouter, Depends

from app.dependencies.tenant import get_current_organization
from app.models.platform.organization import Organization
from app.schemas.organization_schema import PublicOrganizationResponse

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.get("/current", response_model=PublicOrganizationResponse)
def show_current_organization(organization: Organization = Depends(get_current_organization)):
    return organization
