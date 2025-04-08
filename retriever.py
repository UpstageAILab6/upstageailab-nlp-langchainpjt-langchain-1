import os
from vectorstore import VectorDBStore  # VectorDBStore 클래스 import

# HTML 파일 경로 지정
html_path = '/home/data/Langchain/qa_engine_test/data/files/page.html' #os.path.join(os.path.dirname(os.getcwd()), "data/files/page.html")

# VectorDBStore 인스턴스 생성
vectordb_store = VectorDBStore(html_path)

#vectorDB 생성
vectordb_store.load_html()
vectordb_store.load_documents()
vectordb_store.mdtrans()
vectordb_store.split_preprocess_documents()
vectorstore = vectordb_store.create_vectordb()

# retriever 생성(최대 4개의 검색 결과 반환)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})




# 검색 실행
if __name__ == "__main__":
    query = "휴가 폼 알려줘"
    docs = retriever.invoke(query)  # 검색 결과 저장

    # 검색된 문서 출력

    print("\n 검색된 문서:")
    if docs:
        for i, doc in enumerate(docs, 1):
            print(f"\n[{i}]")
            print("내용:", doc.page_content)
            print("메타데이터:", doc.metadata)
    else:
        print("검색 결과가 없습니다.")


