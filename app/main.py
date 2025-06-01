from fastapi import FastAPI
import logging

from app.routes.api import router as api_router
from app.routes.api import initialize_matcher
from app.config.settings import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Automated Audio Response System",
    description="API for matching queries with audios using NLP",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Automated Audio Response System",
        "version": "1.0.0",
        "status": "active"
    }

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting system...")
        initialize_matcher()
        logger.info("System started successfully")
    except Exception as e:
        logger.error(f"Error on startup: {e}")
        raise