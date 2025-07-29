from pathlib import Path
from typing import List, Literal, Union, overload

import fitz  # PyMuPDF


class PDFLoader:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    @overload
    def load_text(self, by_page: Literal[True]) -> List[str]: ...

    @overload
    def load_text(self, by_page: Literal[False]) -> str: ...

    def load_text(self, by_page: bool = False) -> Union[str, List[str]]:
        """
        Extracts text from a PDF using PyMuPDF.
        - If `by_page` is False: returns single concatenated string
        - If `by_page` is True: returns list of page-wise strings
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        with fitz.open(self.file_path) as doc:
            if by_page:
                return [page.get_text() for page in doc]
            else:
                return "\n".join([page.get_text() for page in doc])
