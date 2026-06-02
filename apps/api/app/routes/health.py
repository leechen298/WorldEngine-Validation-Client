from fastapi import APIRouter

from ..config import get_settings
from ..schemas import HealthResponse, HealthWorldEngineResponse
from ..worldengine_client import check_worldengine_health

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="worldengine-validation-client",
        worldengine_api_base=settings.worldengine_api_base,
        database_path=settings.database_path,
    )


@router.get("/health/worldengine", response_model=HealthWorldEngineResponse)
async def worldengine_health() -> HealthWorldEngineResponse:
    worldengine_data = await check_worldengine_health()
    return HealthWorldEngineResponse(
        status="ok" if worldengine_data["reachable"] else "degraded",
        worldengine=worldengine_data,
    )
