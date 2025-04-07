# retriever_test.py (LLM 응답 포함)

from dotenv import load_dotenv
load_dotenv(dotenv_path="/data/ephemeral/home/QA/.env")

from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain.chains import RetrievalQA

# 1. 업스테이지 임베딩 모델 로드
embedding = UpstageEmbeddings(model="solar-embedding-1-large")

# 2. FAISS 벡터 저장소 로드
vectorstore = FAISS.load_local(
    folder_path="/data/ephemeral/home/QA/faiss_store",
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

# 3. LangChain 리트리버 객체 생성
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 4. 사용자 질문 입력
query = input("\n 질문을 입력하세요: ")
docs = retriever.get_relevant_documents(query)

# 5. 유사 문단 출력
for i, doc in enumerate(docs, 1):
    print(f"\n🔎 결과 {i}\n{doc.page_content}")

# 6. LLM QA 체인 생성 및 응답 출력
llm = ChatUpstage()
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

qa_response = qa_chain.invoke({"query": query})

print("\n LLM 응답:")
print(qa_response["result"])
import os
print("🔐 API Key:", os.getenv("UPSTAGE_API_KEY"))