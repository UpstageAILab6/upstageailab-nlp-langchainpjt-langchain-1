import os
from dotenv import load_dotenv
from vectorstore import VectorDBStore  # 벡터DB 클래스 가져오기
from retriever import retriever  # 검색용 retriever 가져오기
from llm import PromptLLM  

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("UPSTAGE_API_KEY")
hb_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def setup_vectorstore():
    """벡터DB를 생성하는 함수"""
    print("벡터DB 생성 중")
    html_path = "/home/data/Langchain/qa_engine_test/data/files/page.html"  # HTML 파일 경로

    # 벡터DB 인스턴스 생성 및 전처리 수행
    vectordb_store = VectorDBStore(html_path)
    vectordb_store.load_html()
    vectordb_store.load_documents()
    vectordb_store.mdtrans()
    vectordb_store.split_preprocess_documents()
    vectorstore = vectordb_store.create_vectordb()

    print("벡터DB 생성 완료")
    return vectorstore


def main():
    print("RAG 실행 중")

    # 벡터DB 설정
    vectorstore = setup_vectorstore()

    # 검색기 생성 (retriever 업데이트)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # LLM 인스턴스 생성
    llm_model = PromptLLM(hb_api_key, retriever)

    while True:
        query = input("\n 질문을 입력하세요 (종료: 'exit'): ")
        if query.lower() == "exit":
            print("프로그램 종료")
            break

        # 검색 및 응답 생성
        response = llm_model.generate_response(query)
        print("\n AI 응답:", response)


if __name__ == "__main__":
    main()



