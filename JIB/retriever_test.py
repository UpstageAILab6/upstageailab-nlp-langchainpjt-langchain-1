# retriever_test.py

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
print(type(vectorstore))
# 3. 리트리버 + QA 체인 구성
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
llm = ChatUpstage()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# 4. 사용자 질문 → LLM 응답
query = input("\n 질문을 입력하세요: ")
qa_response = qa_chain.invoke({"query": query})

# 5. LLM의 답변 출력
print("\n LLM 응답:")
print(qa_response["result"])

# 6. 원문 문단(출처) 출력 (선택 사항)
#print("\n 관련 문단:")
#for i, doc in enumerate(qa_response["source_documents"], 1):
#    print(f"\n 문단 {i}:\n{doc.page_content}")
# 7. 관련 문단 요약 출력 
def summarize_docs(docs):
    summarizer = ChatUpstage()
    summaries = []
    for doc in docs:
        prompt = f"다음 문단을 2~3줄로 요약해줘:\n\n{doc.page_content}"
        response = summarizer.invoke(prompt)
        summaries.append(response.content.strip())
    return summaries

print("\n📄 관련 문단 요약:")
summaries = summarize_docs(qa_response["source_documents"])
for i, summary in enumerate(summaries, 1):
    print(f"\n📘 요약 문단 {i}:\n{summary}")
