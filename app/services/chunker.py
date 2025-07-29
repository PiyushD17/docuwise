from langchain.text_splitter import CharacterTextSplitter


def chunk_texts(pages: list[str]) -> list[str]:
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return [chunk for page in pages for chunk in splitter.split_text(page)]
