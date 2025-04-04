import streamlit as st
from dotenv import load_dotenv
from src.config.env_config import configure_upstage_api
from src.modules.embedding.embedding import load_vector_store_once
# from src.modules.init import init


from src.modules.model.chat import get_response
from src.modules.prompt.template import build_prompt
from src.modules.vector_store.vector_db import search_vector_store


def extract_context_and_files(result):
    """
    검색 결과에서 중복 없이 context와 attached_file 정보를 추출합니다.
    """
    unique_context = []
    unique_attached_files = set()

    for chunk in result:
        content_text = chunk.page_content
        source = chunk.metadata.get("source", "Unknown")
        context_entry = f"source: {source} , contents: {content_text}"
        if context_entry not in unique_context:
            unique_context.append(context_entry)

        for file in chunk.metadata.get("attached_file", []):
            unique_attached_files.add(file)

    combined_context = "\n\n".join(unique_context)
    attached_files_str = "\n".join(sorted(unique_attached_files)) if unique_attached_files else "None"

    print(f"Combined Context: {combined_context}")
    return combined_context, attached_files_str


def main(vector_store):
    """
    vector_store 인스턴스를 인자로 받아 Streamlit 앱을 실행합니다.
    """
    # 환경 변수 설정을 별도 모듈을 통해 수행
    if not configure_upstage_api():
        return

    st.title("Academy QA Bot")

    # 사용자로부터 질문 입력 받기
    query = st.text_input("질문을 입력하세요", "휴가 사유는 어떻게 작성하나요?")

    if st.button("답변 받기"):
        with st.spinner("답변을 생성 중입니다..."):
            result = search_vector_store(vector_store, query)
            combined_context, attached_files_str = extract_context_and_files(result)
            prompt = build_prompt(combined_context, attached_files_str, query)
            response = get_response(prompt, combined_context)
            st.subheader("LLM의 응답")
            st.write(response.content)


if __name__ == "__main__":
    # 필요에 따라 초기화 함수 호출
    # init()
    load_dotenv()

    vector_store = load_vector_store_once()
    main(vector_store)
