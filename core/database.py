import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import Base

logger = logging.getLogger(__name__)


class Database:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./image_data.db"

    def __init__(self):
        logger.info("Initializing database engine.")
        self.engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_db(self):
        logger.info("Creating database tables.")
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_db(self):
        logger.debug("Creating a new database session.")
        session = self.session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            logger.debug("Database session closed.")


SessionLocal = Database().session_local
