import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app, Database, ImageProcessor
from models import Image as ImageModel

test_db = Database()
test_image_processor = ImageProcessor('tests/test_data/img.csv')

test_db.init_db()
with test_db.get_db() as session:
    test_image_processor.process_images(session)


@pytest.fixture(scope="module")
def test_db_instance():
    db = Database()
    db.init_db()
    yield db


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def test_image_processor_instance():
    yield test_image_processor


@pytest.fixture(scope="module")
def test_image_directory():
    return 'tests/test_data/images'
