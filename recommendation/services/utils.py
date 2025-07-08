from despsharedlibrary.schemas.collaborative_schema import AssetType, SourceType
from msfwk.utils.logging import get_logger

from recommendation.models.interfaces import RecommendableDocument, RecommendAssetList, SearchQuery

logger = get_logger(__name__)


def merge_asset_dicts(assets_per_top: dict[str, RecommendAssetList]) -> list[RecommendableDocument]:
    """Merge all the assets in the top-k. If an asset is present in multiple top-k, the r_score is summed."""
    all_assets = {}
    for assets in assets_per_top.values():
        for asset in assets.assets:
            if asset.id not in all_assets:
                all_assets[asset.id] = asset
            else:
                all_assets[asset.id].r_score += asset.r_score
    return list(all_assets.values())


def get_k_best_r_score(assets: list[RecommendableDocument], offset: int, limit: int) -> list[RecommendableDocument]:
    """Get the k best r_score assets"""
    logger.debug("assets: %s", {asset.name: asset.r_score for asset in assets})
    return sorted(assets, key=lambda x: x.r_score, reverse=True)[offset : offset + limit]


def build_query(
    q: str = "", asset_type: AssetType | None = None, source: SourceType | None = None, categories: str | None = None
) -> SearchQuery:
    """Build a query from the given args"""
    return SearchQuery(
        text=q,
        documentType=asset_type,
        documentSource=source,
        documentCategory=categories.split(",") if categories else None,
    )
