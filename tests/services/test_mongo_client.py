from datetime import datetime
from unittest.mock import patch

import pytest

from app.services import mongo_client
from app.services.mongo_client import metadata_collection, save_metadata


def test_save_metadata_inserts_document() -> None:
    dummy_metadata = {
        "filename": "test.pdf",
        "user_id": "test_user",
        "upload_time": datetime.utcnow(),
        "file_path": "/data/test.pdf",
        "size": 1024,
    }

    with patch.object(
        mongo_client, "metadata_collection", autospec=True
    ) as mock_collection:
        mongo_client.save_metadata(dummy_metadata)
        mock_collection.insert_one.assert_called_once_with(dummy_metadata)


@pytest.fixture
def test_document() -> dict:
    return {
        "filename": "integration_test.pdf",
        "user_id": "test_user_987",
        "upload_time": datetime.utcnow(),
        "file_path": "/data/integration_test.pdf",
        "size": 55555,
    }


def test_save_metadata_inserts_into_real_mongodb(test_document: dict) -> None:
    # Cleanup first in case of previous runs
    metadata_collection.delete_many({"user_id": test_document["user_id"]})

    # Save using the service method
    save_metadata(test_document)

    # Verify it was saved
    found = metadata_collection.find_one({"user_id": test_document["user_id"]})
    assert found is not None
    assert found["filename"] == test_document["filename"]

    # Optional cleanup
    metadata_collection.delete_many({"user_id": test_document["user_id"]})
