from langchain_community.document_transformers import MarkdownifyTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.modules.db.vector_db import FaissDB
from src.modules.embedding.embedding import Embedding
from src.modules.loader.notion_loader import NotionLoader, LawLoader


def init():
    notion_url = "https://sincere-nova-ec6.notion.site/a8bbcb69d87c4c19aabee16c6a178286"
    loader = NotionLoader()
    document = loader.load(notion_url)
    md = MarkdownifyTransformer()
    converted_docs = md.transform_documents([document])
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
        # separators=["\n\n", "\n"],
    )
    chunked_docs = text_splitter.split_documents(converted_docs)
    if document is not None:
        embeddings = Embedding()
        db = FaissDB(embeddings.model, persist_directory="./faiss")
        db.add_documents(chunked_docs)

