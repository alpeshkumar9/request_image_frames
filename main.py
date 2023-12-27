import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from core.logger import LOGGING
from settings import settings
from core.image_processor import ImageProcessor
from core.database import Database

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI()
db = Database()
image_processor = ImageProcessor('data/img.csv')


def get_db():
    with db.get_db() as session:
        yield session


@app.on_event("startup")
async def startup_event():
    """Initializes the database and processes images on application startup."""
    db.init_db()
    with db.get_db() as session:
        image_processor.process_images(session)


@app.get("/images/")
def get_images(depth_min: float, depth_max: float, db: Session = Depends(get_db)):
    """Fetches images within a specified depth range."""
    try:
        images = image_processor.get_images_by_depth_range(
            db, depth_min, depth_max)
        image_urls = [
            {"depth": depth, "url": image_processor.save_image_to_file(
                image, depth)}
            for depth, image in images
        ]
        return image_urls
    except Exception as e:
        logger.error(f"Failed to get images: {e}")
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_config=LOGGING,
        log_level=settings.log_level.lower(),
        reload=True
    )
