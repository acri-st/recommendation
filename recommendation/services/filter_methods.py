from msfwk.utils.logging import get_logger

from recommendation.filters.filter_holder import filters_apply
from recommendation.filters.search_filters import SearchFilter
from recommendation.models.interfaces import (
    RecommendableDocument,
)
from recommendation.services.utils import get_k_best_r_score

logger = get_logger("application")


async def recommend(
    filters: list[SearchFilter],
    offset: int = 0,
    limit: int = 8,
) -> tuple[list[RecommendableDocument], int]:
    """Get content-based recommendations for a given query

    Args:
        filters (list[SearchFilter]): all the filters to apply
        offset (int, optional): Number of results to skip. Defaults to 0.
        limit (int, optional): Number of results to return. Defaults to 8.

    Returns:
        list[RecommendableDocument]: List of recommended assets
        int: nb of recommended assets
    """
    assets = await filters_apply(filters)
    return get_k_best_r_score(assets, offset, limit), len(assets)
