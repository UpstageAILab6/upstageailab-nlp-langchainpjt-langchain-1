import os
from dotenv import load_dotenv
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain.prompts import ChatPromptTemplate

from src.modules.init import init

def load_vector_store_once(faiss_dir: str = "faiss"):
    """
    FAISS 벡터스토어를 한 번 로드하여 반환합니다.
    """
    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    vector_store_instance = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
    return vector_store_instance

def search_vector_store(vector_store, query: str):
    """
    전달받은 vector_store 인스턴스를 사용하여 주어진 질의(query)로 유사 청크를 검색합니다.
    """
    result = vector_store.similarity_search(query)
    return result

def extract_context_and_files(result):
    """
    검색 결과에서 중복 없이 context와 attached_file 정보를 추출합니다.
    """
    unique_context = []
    unique_attached_files = set()  # 중복 제거를 위해 set 사용

    for chunk in result:
        content_text = chunk.page_content
        source = chunk.metadata.get("source", "Unknown")
        context_entry = f"source: {source} , contents: {content_text}"
        if context_entry not in unique_context:
            unique_context.append(context_entry)

        # 각 청크의 attached_file 리스트에서 중복 없이 파일명 추가
        for file in chunk.metadata.get("attached_file", []):
            unique_attached_files.add(file)

    combined_context = "\n\n".join(unique_context)
    attached_files_str = "\n".join(sorted(unique_attached_files)) if unique_attached_files else "None"

    print(f"Combined Context: {combined_context}")
    return combined_context, attached_files_str

def build_prompt(context: str, attached_files: str, query: str):
    """
    주어진 context, 첨부 파일 정보와 질의를 바탕으로 Langchain ChatPromptTemplate을 생성합니다.
    """
    messages = [
        (
            "system",
            (
                "You are an academy QA bot. The questioner is \"AI+Lab_7기(Upstage_AI+6기)\". "
                "Your role is to answer questions about academic policies and procedures, including leave applications. "
                "Thoroughly analyze the provided context and extract all relevant details. When referring to additional resources, "
                "explicitly include:\n- The names of any attached files (e.g., files with a '.docx' extension)\n"
                "- Their corresponding source links as provided in the context.\n"
                "If the context does not contain complete information but relevant attached files are available, instruct the user to consult these documents for further details.\n"
                "Additionally, format your answer using bullet points to enhance readability and ensure that source links are always included."
            )
        ),
        (
            "system",
            f"Here is the context you must reference:\n{context}"
        ),
        (
            "system",
            f"The following attached files may contain additional details:\n{attached_files}"
        ),
        (
            "human",
            f"Using the above context and attached file information, answer the following question comprehensively:\n\n{query}"
        ),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt

def get_response(prompt, context: str):
    """
    ChatUpstage 인스턴스를 이용하여 최종 응답을 받아옵니다.
    """
    chat = ChatUpstage()
    chain = prompt | chat
    response = chain.invoke({"context": context})
    return response

def main(vector_store):
    """
    vector_store 인스턴스를 인자로 받아 Streamlit 앱을 실행합니다.
    """
    # .env 파일을 로드하여 환경변수를 설정
    load_dotenv()
    upstage_api_key = os.getenv("UPSTAGE_API_KEY")
    if not upstage_api_key:
        st.error("UPSTAGE_API_KEY가 설정되어 있지 않습니다. .env 파일에 해당 변수를 추가해주세요.")
        return
    os.environ["UPSTAGE_API_KEY"] = upstage_api_key

    st.title("Academy QA Bot")

    # 사용자로부터 질문 입력 받기
    query = st.text_input("질문을 입력하세요", "휴가 사유는 어떻게 작성하나요?")

    if st.button("답변 받기"):
        with st.spinner("답변을 생성 중입니다..."):
            # 1. 전달받은 vector_store 인스턴스를 사용하여 검색 수행
            result = search_vector_store(vector_store, query)
            # 2. 검색 결과에서 context와 첨부파일 정보 추출
            combined_context, attached_files_str = extract_context_and_files(result)
            # 3. 프롬프트 생성
            prompt = build_prompt(combined_context, attached_files_str, query)

            # 중간 결과 디버그 출력 (필요에 따라 주석 처리 가능)
            # st.subheader("Combined Context")
            # st.code(combined_context)
            # st.subheader("Attached Files")
            # st.write(attached_files_str)

            # 4. LLM 응답 호출
            response = get_response(prompt, combined_context)

            st.subheader("LLM의 응답")
            st.write(response.content)

if __name__ == "__main__":
    # 필요에 따라 초기화 함수 호출
    # init()
    vector_store = load_vector_store_once()
    main(vector_store)