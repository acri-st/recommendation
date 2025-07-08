import json
from datetime import datetime
from typing import Any

from despsharedlibrary.schemas.collaborative_schema import AssetType, SourceType
from msfwk.utils.logging import get_logger
from pydantic import BaseModel, ConfigDict

logger = get_logger(__name__)
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"  # +00:00 comes from UTC


class SearchableDocument(BaseModel):
    """Class describing a document that will be registered to the index"""

    # The id of the asset in the relational database
    id: str
    # The type that will drive the index to use
    documentType: AssetType  # noqa: N815
    # The name of the asset
    name: str
    # Meta data about the asset to be indexed
    metadata: dict[str, str]
    date: datetime
    # Search score the closer it gets to 1, the closer is from the search
    score: float = 0.0
    # Asset category
    categoryId: str  # noqa: N815
    # source of the asset
    source: SourceType = SourceType.user
    # nb of likes
    likes_count: int
    downloads_count: int = -1

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            AssetType: lambda at: at.value,
            SourceType: lambda st: st.value,
        }
    )

    def to_dict(self) -> dict[str, str]:
        """Make the class serializable"""
        return {
            "id": self.id,
            "name": self.name,
            "metadata": json.dumps(self.metadata),  # TODO: once we know the metadata change it back to an object
            "date": self.date.isoformat(),
            "type": self.documentType.value,
            "categoryId": self.categoryId,
            "source": self.source.value,
            "likes_count": self.likes_count,
            "downloads_count": self.downloads_count,
        }


class RecommendableDocument(SearchableDocument):
    """Contains the recommendation score of the document"""

    r_score: float = 0.0


class SearchModel(BaseModel):
    """Hold the result of a search"""

    count: int
    assets: list[SearchableDocument]

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            AssetType: lambda at: at.value,
            SourceType: lambda st: st.value,
        }
    )

    def __init__(self, assets: list[SearchableDocument], count: int | None = None) -> None:
        """Build the SearchResults based on the assets dictionary"""
        if count is None:
            super().__init__(assets=assets, count=len(assets))
        else:
            super().__init__(assets=assets, count=count)


class RecommendAssetList(BaseModel):
    """Hold the result of a search"""

    count: int
    assets: list[RecommendableDocument]

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            AssetType: lambda at: at.value,
            SourceType: lambda st: st.value,
        }
    )

    def __init__(self, assets: list[RecommendableDocument], count: int | None = None) -> "RecommendAssetList":
        """Build the SearchResponse based on the assets list"""
        super().__init__(assets=assets, count=count if count is not None else len(assets))


class SearchQuery(BaseModel):
    """hold the search criteria"""

    documentType: AssetType | None = None  # noqa: N815
    documentSource: SourceType | None = None  # noqa: N815
    documentCategory: list[str] | None = None  # noqa: N815
    metadatas: dict[str, int | str] | None = None
    text: str

    model_config = ConfigDict(json_encoders={AssetType: lambda at: at.value, SourceType: lambda st: st.value})


class SortQuery(BaseModel):
    """hold the sort criteria"""

    field: str
    order: str

    def to_es_format(self) -> dict[str, str]:
        """Convert the sort to the es format"""
        return {self.field: {"order": self.order}}


class MultiSearchQuery(BaseModel):
    """Hold multiple search criteria with different sort orders"""

    queries: dict[str, tuple[SearchQuery, list[SortQuery]]]
    limit: int

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            AssetType: lambda at: at.value,
            SourceType: lambda st: st.value,
        }
    )


class ToRecommendResponse(BaseModel):
    """Hold the result of a multi-search"""

    results: dict[str, RecommendAssetList]

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            AssetType: lambda at: at.value,
            SourceType: lambda st: st.value,
        }
    )


class ExtractedField(BaseModel):
    """Contains the fields to extract from the search response"""

    name: str
    ponderation: float = 1.0


class ServiceCall(BaseModel):
    """Contains the service call to be made"""

    route_call: str
    service_call: str
    payload: dict[str, Any] | None = None

    def same_call(self, other: object) -> bool:
        """Check if the service call is equal to another service call"""
        if not isinstance(other, ServiceCall):
            return False
        return self.route_call == other.route_call and self.service_call == other.service_call
