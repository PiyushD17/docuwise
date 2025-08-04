from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_pdf_route_success() -> None:
    test_file = Path("tests/data/sample.pdf")
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/upload", files={"file": ("sample.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "sample.pdf"
    assert data["saved_as"].endswith(".pdf")
    assert data["storage"] == "local"
