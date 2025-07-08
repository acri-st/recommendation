from despsharedlibrary.schemas.collaborative_schema import AssetType, SourceType
from fastapi import APIRouter
from msfwk.application import openapi_extra
from msfwk.models import BaseDespResponse, DespResponse
from msfwk.utils.logging import get_logger
from pydantic import BaseModel

from recommendation.filters.filter_holder import filters_get, filters_regenerate
from recommendation.models.constants import (
    FAILED_TO_RECOMMEND_ASSET,
    MISSING_TYPE_IN_REQUEST,
)
from recommendation.models.exceptions import RecommendationFailedError
from recommendation.models.interfaces import RecommendAssetList
from recommendation.services.filter_methods import recommend
from recommendation.services.utils import build_query

__all__ = ["router"]

router = APIRouter()
logger = get_logger(__name__)


class RequestBody(BaseModel):
    name: str
    description: str


@router.get(
    "/recommend",
    summary="recommend from search based on criteria",
    response_model=BaseDespResponse[RecommendAssetList],
    response_description="The list of assets matching the criteria",
    tags=["search"],
    openapi_extra=openapi_extra(secured=False, roles=[]),
)
async def recommend_assets(  # noqa: PLR0913
    q: str = "",
    type: AssetType | None = None,  # noqa: A002
    categories: str | None = None,  # noqa: ARG001
    source: SourceType | None = None,
    offset: int = 0,  # noqa: ARG001
    limit: int = 10,  # noqa: ARG001
) -> DespResponse[RecommendAssetList]:
    """Recommend"""
    logger.info("Recommending assets... with q=%s, type=%s, source=%s", q, type, source)
    if type is None:
        message = "Missing type in the request. Consider using type={dataset/model/paper/application/other}"
        logger.error(message)
        return DespResponse(
            data={},
            error=message,
            code=MISSING_TYPE_IN_REQUEST,
            http_status=400,
        )
    try:
        query = build_query(q, type, source, categories)
        if not filters_regenerate(query):
            logger.error("Failed to build filters for recommendations")
            return DespResponse(
                data=RecommendAssetList(assets=[]).model_dump(mode="json"),
                error=str(e),
                code=FAILED_TO_RECOMMEND_ASSET,
                http_status=500,
            )
        filters = filters_get()
        recommended_assets, tot_recommended_assets = await recommend(filters, offset, limit)
        logger.debug("Found assets: %s", recommended_assets)
        return DespResponse(
            data=RecommendAssetList(assets=recommended_assets, count=tot_recommended_assets).model_dump(mode="json")
        )
    except RecommendationFailedError as e:
        logger.exception("Failed to perform recommendation for", exc_info=e)
        return DespResponse(
            data=RecommendAssetList(assets=[]).model_dump(mode="json"),
            error=str(e),
            code=FAILED_TO_RECOMMEND_ASSET,
            http_status=500,
        )
