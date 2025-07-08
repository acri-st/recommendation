import asyncio
from typing import Any

import aiohttp
from msfwk.utils.logging import get_logger
from pydantic import BaseModel

from recommendation.filters.utils import normalize_and_ponderate_r_score
from recommendation.models.interfaces import RecommendAssetList, ToRecommendResponse

logger = get_logger(__name__)


class AbstractFilter(BaseModel):
    """Abstract class for filters"""

    filter_name: str
    url: str
    http_method: str = "GET"
    payload: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    ponderation: float

    async def apply(self) -> dict[str, RecommendAssetList] | None:
        """Apply the filter by calling the service API."""
        try:
            async with aiohttp.ClientSession() as session:
                if self.http_method == "GET":
                    async with session.get(self.url, headers=self.headers, params=self.payload) as response:
                        return await self._handle_response(response)

                elif self.http_method == "POST":
                    response = await session.post(
                        self.url,
                        json=self.payload,
                    )
                    if (asset_dict := await self._handle_response(response)) is not None:
                        return await self._apply_norm_and_pond(asset_dict)

                elif self.http_method in {"POST", "PUT", "PATCH", "DELETE"}:
                    logger.debug("Use %s on %s with payload: %s ", self.http_method, self.url, self.payload)
                    async with getattr(session, self.http_method.lower())(
                        self.url, headers=self.headers, data=str(self.payload)
                    ) as response:
                        if (asset_dict := await self._handle_response(response)) is not None:
                            return await self._apply_norm_and_pond(asset_dict)
                else:
                    logger.error("Unsupported HTTP method: %s", self.http_method)
                    return None

        except aiohttp.ClientError as ce:
            message = f"HTTP client error during apply() in filter '{self.filter_name}': {ce}"
            logger.exception(message, exc_info=ce)
        except asyncio.TimeoutError as te:
            message = f"Timeout during apply() in filter '{self.filter_name}': {te}"
            logger.exception(message, exc_info=te)
        return None

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict[str, RecommendAssetList] | None:
        if response.status >= 300:
            logger.warning("Filter '%s' returned status %s", self.filter_name, response.status)
            return None
        try:
            data = (await response.json()).get("data")
            # check validity
            return ToRecommendResponse(**data).results
        except Exception as ee:
            message = f"Failed to parse JSON response for filter '{self.filter_name}': {ee}"
            logger.exception(message, exc_info=ee)
            return None

    async def _apply_norm_and_pond(self, asset_dict: dict[str, RecommendAssetList]) -> dict[str, RecommendAssetList]:
        """Normalize and ponderate

        Args:
            asset_dict (dict[str, list[RecommendAssetList]]): _description_
        """
        for key in asset_dict:
            normalize_and_ponderate_r_score(key, self.ponderation, asset_dict[key])
        return asset_dict
