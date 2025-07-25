from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


def main():
    # 1) Load the PDF
    loader = PyPDFLoader("data/sample.pdf")
    docs = loader.load()
    print(f"Loaded {len(docs)} pages")

    # 2) Split into chunks
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks\n")

    # 3) Preview the first few chunks
    for i, chunk in enumerate(chunks[0:3], start=1):
        text = chunk.page_content.replace("\n", " ")
        preview = text[:200]
        print(f"Chunk {i} preview: “{preview}…”\n")


if __name__ == "__main__":
    main()
