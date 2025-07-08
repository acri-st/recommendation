from recommendation.filters.search_filters import SearchFilter
from recommendation.models.interfaces import ExtractedField

FAILED_TO_RECOMMEND_ASSET = 19001
MISSING_TYPE_IN_REQUEST = 19002

TOP_K_RECOMMENDATIONS = 20
TOP_K_FIELDS = {
    "likes_count": ExtractedField(name="likes_count", ponderation=3),
    "downloads_count": ExtractedField(name="downloads_count", ponderation=2),
}

FILTERS = [SearchFilter]
