from msfwk.utils.logging import get_logger

from recommendation.filters.abstract_filter import AbstractFilter
from recommendation.filters.search_filters import SearchFilter
from recommendation.models.exceptions import MissingConfigError
from recommendation.models.interfaces import RecommendableDocument, SearchQuery
from recommendation.services.utils import merge_asset_dicts

logger = get_logger(__name__)

filter_holder = []


def filters_regenerate(query: SearchQuery) -> bool:
    r"""Clean and adds to the filter_holder the wanted filters.
    /!\ Should be modified when reco not present during a search /!\
        - Remove query (will no longer be needed)
        - genereate only once each filter, (in the init container)

    Args:
        query (SearchQuery): _description_

    Returns:
        bool: _description_
    """
    filters_clean()
    try:
        filters = [SearchFilter.from_query(query)]
        filters_add(filters)
    except MissingConfigError as mce:
        message = "Missing element in config"
        logger.exception(message, exc_info=mce)
        return False
    return True


def filters_get() -> list[AbstractFilter]:
    """Return the list of all current filters"""
    return filter_holder


def filters_add(filters: list[AbstractFilter]) -> None:
    """Add new filters in the filter_holder"""
    filter_holder.extend(filters)


def filters_clean() -> None:
    """Clean all the element in the filter_holder"""
    filter_holder.clear()


async def filters_apply(filters: list[AbstractFilter]) -> list[RecommendableDocument]:
    """Return the list of all potential recommendations, compute based on the recommendation from each filters"""
    asset_dict = {}
    for curr_filter in filters:
        if (filter_result := await curr_filter.apply()) is None:
            logger.warning("Filter %s returns nothing", curr_filter.filter_name)
        else:
            asset_dict.update(filter_result)

    return merge_asset_dicts(asset_dict)
