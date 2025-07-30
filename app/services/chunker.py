from typing import List


class TextChunker:
    """
    A utility class to split long texts into overlapping chunks,
    useful for embedding and vector indexing in NLP pipelines.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the chunker.

        Args:
            chunk_size (int): Maximum number of characters in a chunk.
            overlap (int): Number of overlapping characters between consecutive chunks.

        Raises:
            ValueError: If chunk_size is not greater than overlap.
        """
        if chunk_size <= overlap:
            raise ValueError("chunk size must be greater than overlap")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, pages: List[str]) -> List[str]:
        """
        Splits a list of page-level text strings into overlapping chunks.

        Args:
            pages (List[str]): List of text strings, typically one per page.

        Returns:
            List[str]: List of text chunks with overlap applied.
        """
        chunks = []
        for page in pages:
            if not page.strip():
                continue
            chunks.extend(self._split_with_overlap(page))
        return chunks

    def _split_with_overlap(self, text: str) -> List[str]:
        """
        Internal helper to split a single string into chunks with overlap.

        Args:
            text (str): The full string to split.

        Returns:
            List[str]: List of overlapping chunks from the input text.
        """
        start = 0
        end = self.chunk_size
        text_length = len(text)
        results = []

        while start < text_length:
            results.append(text[start:end])
            start = end - self.overlap
            end = start + self.chunk_size
        return results
