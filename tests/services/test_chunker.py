import pytest

from app.services.chunker import TextChunker


def test_chunker_splits_text_with_overlap():
    text = "abcdefghij" * 100  # 1000 characters
    pages = [text]
    chunker = TextChunker(chunk_size=200, overlap=50)
    chunks = chunker.chunk(pages)

    # Check that we got multiple chunks
    assert len(chunks) > 1

    # Check chunk lengths and overlap
    for i in range(len(chunks)):
        assert len(chunks[i]) <= 200
        if i > 0:
            # Ensure overlap exists
            assert chunks[i][:50] == chunks[i - 1][-50:]


def test_chunker_skips_empty_pages():
    pages = ["This is page one.", "", "    ", "\n", "This is page two."]
    chunker = TextChunker(chunk_size=50, overlap=10)
    chunks = chunker.chunk(pages)

    # Only 2 non-empty pages should be processed
    assert all("page" in chunk for chunk in chunks)
    assert len(chunks) >= 2


def test_chunker_raises_on_invalid_config():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=100)  # Invalid: chunk_size <= overlap


def test_chunker_exact_boundary():
    text = "a" * 1000
    chunker = TextChunker(chunk_size=200, overlap=0)
    chunks = chunker.chunk([text])

    assert all(len(chunk) == 200 for chunk in chunks[:-1])
    assert len("".join(chunks)) == 1000


def test_chunker_handles_short_texts():
    short_text = "short text"
    chunker = TextChunker(chunk_size=100, overlap=10)
    chunks = chunker.chunk([short_text])

    assert len(chunks) == 1
    assert chunks[0] == short_text
