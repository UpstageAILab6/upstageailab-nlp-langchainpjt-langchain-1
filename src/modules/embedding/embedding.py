import os

from langchain_upstage import UpstageEmbeddings

class Embedding:
    """
    Upstage Embeddings wrapper for Langchain.
    """

    def __init__(self):
        self.model = UpstageEmbeddings(model="solar-embedding-1-large")

    def embed_documents(self, texts):
        # Implement the logic to embed documents using Upstage API
        pass

    def embed_query(self, text):
        # Implement the logic to embed a query using Upstage API
        pass
