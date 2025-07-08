from msfwk.application import app
from msfwk.utils.logging import get_logger

from recommendation.routes.recommend import router as recommend_router

logger = get_logger("application")

app.include_router(recommend_router)
