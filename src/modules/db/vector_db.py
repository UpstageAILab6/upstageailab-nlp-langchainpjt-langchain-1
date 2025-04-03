from abc import ABC, abstractmethod
from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS


class VectorDB(ABC):
    @abstractmethod
    def create_store(self, docs: List[Document]):
        """문서 리스트를 사용하여 벡터 스토어를 생성합니다."""
        pass

    @abstractmethod
    def add_documents(self, docs: List[Document]):
        """기존 벡터 스토어에 문서를 추가합니다."""
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """주어진 쿼리와 유사한 문서를 검색합니다."""
        pass


class FaissDB(VectorDB):
    def __init__(self, embeddings):
        """
        FAISS 기반 벡터 스토어 구현체입니다.

        Args:
            embeddings: 외부에서 주입된 임베딩 인스턴스.
        """
        self.embeddings = embeddings
        self.vectorstore = None

    def create_store(self, docs: List[Document]):
        """
        주어진 문서 리스트를 사용하여 FAISS 벡터 스토어를 생성합니다.

        Args:
            docs (List[Document]): 문서 객체 리스트.
        """
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)

    def add_documents(self, docs: List[Document]):
        """
        벡터 스토어에 문서를 추가합니다. 아직 생성되지 않았다면, 먼저 벡터 스토어를 생성합니다.

        Args:
            docs (List[Document]): 문서 객체 리스트.
        """
        if self.vectorstore is None:
            self.create_store(docs)
        else:
            self.vectorstore.add_documents(docs)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        주어진 쿼리와 유사한 문서를 검색합니다.

        Args:
            query (str): 검색할 쿼리 문자열.
            k (int, optional): 반환할 문서 개수 (기본값: 4).

        Returns:
            List[Document]: 유사도 순으로 정렬된 문서 객체 리스트.
        """
        if self.vectorstore is None:
            raise ValueError("벡터 스토어가 초기화되지 않았습니다. 먼저 문서를 추가해주세요.")
        return self.vectorstore.similarity_search(query, k=k)

#
# # 모듈 테스트 및 사용 예제
# if __name__ == '__main__':
#     # 예제 문서 생성
#     docs = [
#         Document(page_content="첫 번째 문서의 내용입니다.", metadata={"source": "문서1"}),
#         Document(page_content="두 번째 문서의 내용입니다.", metadata={"source": "문서2"}),
#         Document(page_content="세 번째 문서의 내용입니다.", metadata={"source": "문서3"})
#     ]
#
#     # OpenAIEmbeddings 인스턴스 생성 (YOUR_OPENAI_API_KEY를 실제 키로 교체)
#     embeddings = OpenAIEmbeddings(openai_api_key="YOUR_OPENAI_API_KEY")
#
#     # FAISS 구현체를 활용한 벡터 스토어 초기화
#     db = FaissDB(embeddings)
#
#     # 문서를 이용하여 벡터 스토어 생성
#     db.create_store(docs)
#
#     # 유사도 검색 수행
#     query = "첫 번째 문서"
#     results = db.similarity_search(query)
#
#     print("검색 결과:")
#     for doc in results:
#         print(f"내용: {doc.page_content}, 메타데이터: {doc.metadata}")