from langchain_community.document_loaders import PyPDFLoader


def main():
    loader = PyPDFLoader("data/sample.pdf")
    docs = loader.load()
    print(f"Loaded {len(docs)} pages")
    for i, doc in enumerate(docs, start=1):
        preview = doc.page_content[:200].replace("\\n", " ")
        print(f"Page {i} preview: “{preview}…”")


if __name__ == "__main__":
    main()
