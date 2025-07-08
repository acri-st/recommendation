class SeachServiceError(Exception):
    """An Error occured during the connectoin with the search service"""


class MissingDataError(Exception):
    """Missing data field in API response"""


class MissingConfigError(Exception):
    """Missing element from config"""


class RecommendationFailedError(Exception):
    """Global error for recommendation failed"""
