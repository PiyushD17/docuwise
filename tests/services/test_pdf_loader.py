from pathlib import Path

import pytest

from app.services.pdf_loader import PDFLoader

TEST_PDF = Path("tests/data/sample.pdf")


@pytest.fixture
def loader():
    return PDFLoader(TEST_PDF)


def test_file_exists(loader):
    assert loader.file_path.exists()


def test_load_text_returns_string(loader):
    text = loader.load_text()
    assert isinstance(text, str)
    assert len(text) > 0


def test_load_text_by_page(loader):
    pages = loader.load_text(by_page=True)
    assert isinstance(pages, list)
    assert all(isinstance(p, str) for p in pages)
    assert len(pages) > 0
