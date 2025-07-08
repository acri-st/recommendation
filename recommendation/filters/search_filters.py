"""_Here are defined the filters that uses search services to make recommendation.
We are using only 1 APi request to the search service (using multi-search API)

This requierement implies some modification on the SearchFilter class:
- The SearchFilter is composed of multiple minor_filters.
- It's norm_and_pond methode is modified so it use the ponderation of each minor_filters
"""

from msfwk.context import current_config
from msfwk.utils.logging import get_logger
from pydantic import BaseModel

from recommendation.filters.abstract_filter import AbstractFilter
from recommendation.filters.utils import normalize_and_ponderate_r_score
from recommendation.models.exceptions import MissingConfigError
from recommendation.models.interfaces import (
    MultiSearchQuery,
    RecommendAssetList,
    SearchQuery,
    SortQuery,
)

logger = get_logger(__name__)


class MinorSearchFilter(BaseModel):
    """One of the filter to operate on the Search service"""

    filter_name: str
    ponderation: float
    sorts: list[SortQuery]


class MostDownloadedFilter(MinorSearchFilter):
    """Filter for the most downloaded assets"""

    filter_name: str = "downloads_count"
    ponderation: float = 2.0
    sorts: list[SortQuery] = [SortQuery(field="downloads_count", order="desc")]


class MostLikedFilter(MinorSearchFilter):
    """Filter for the most liked assets"""

    filter_name: str = "likes_count"
    ponderation: float = 2.0
    sorts: list[SortQuery] = [SortQuery(field="likes_count", order="desc")]


class SearchFilter(AbstractFilter):
    """Filter for the search"""

    filter_name: str = "Global Search Filter"
    ponderation: float = 1.0
    minor_filters: dict[str, MinorSearchFilter]

    @classmethod
    def from_query(cls, query: SearchQuery) -> "SearchFilter":
        """Build object from query"""
        search_service_url = current_config.get().get("services", {}).get("search", {}).get("host")
        if search_service_url is None:
            message = "Missing search url from config"
            logger.error(message)
            raise MissingConfigError(message)

        most_downloaded_filter = MostDownloadedFilter()
        most_liked_filter = MostLikedFilter()
        minor_filters = {
            most_downloaded_filter.filter_name: most_downloaded_filter,
            most_liked_filter.filter_name: most_liked_filter,
        }

        payload = MultiSearchQuery(queries={m.filter_name: (query, m.sorts) for m in minor_filters.values()}, limit=20)

        return cls(
            url=search_service_url + "/" + "multi-search",
            http_method="POST",
            payload=payload.model_dump(mode="json"),
            minor_filters=minor_filters,
        )

    async def _apply_norm_and_pond(self, asset_dict: dict[str, RecommendAssetList]) -> dict[str, RecommendAssetList]:
        """Normalize and ponderate

        Args:
            asset_dict (dict[str, list[RecommendAssetList]]): _description_
        """
        for filter_name in self.minor_filters:
            if (asset_list := asset_dict.get(filter_name)) is not None:
                normalize_and_ponderate_r_score(filter_name, self.ponderation, asset_list)
        return asset_dict
