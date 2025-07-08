from msfwk.utils.logging import get_logger

from recommendation.models.interfaces import RecommendAssetList

logger = get_logger(__name__)


def normalize_and_ponderate_r_score(
    normalize_field: str, ponderation: float, asset_list: RecommendAssetList
) -> RecommendAssetList:
    """Normalize and Ponderate the assets based on the field_to_ponderate
    Modify in place the asset_list
    """
    logger.debug("Start Normalization and Ponderation of recommendable assets")
    if len(asset_list.assets) == 0:
        return asset_list

    # Get the max value of the field_to_ponderate
    max_value = (
        max(asset_list.assets, key=lambda asset: asset.to_dict().get(normalize_field, 0))
        .to_dict()
        .get(normalize_field, 0)
    )
    max_value = max(max_value, 0.01)
    logger.debug("max_value of %s for normalization: %s", normalize_field, max_value)

    # Normalize and Ponderate the assets
    for asset in asset_list.assets:
        asset.r_score += (asset.to_dict().get(normalize_field, 0) / max_value) * ponderation

    logger.debug("all ponderated r_scores: %s", {asset.id: asset.r_score for asset in asset_list.assets})
    return asset_list
