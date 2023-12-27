from sqlalchemy import Column, Float, LargeBinary
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Image(Base):
    __tablename__ = 'images'
    depth = Column(Float, primary_key=True)
    image = Column(LargeBinary)
