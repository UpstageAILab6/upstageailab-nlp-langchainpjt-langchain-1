import json
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import streamlit as st

from langchain.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

from src.config.env_config import configure_upstage_api
from src.modules.embedding.embedding import load_vector_store_once
from src.modules.model.chat import get_response
from src.modules.vector_store.vector_db import Faiss, search_vector_store


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

    # print(f"Combined Context: {combined_context}")
    return combined_context, attached_files_str


# 본 예시에서는 "category"를 휴가, 시간표, 법령 중 하나로 예측하는 모델을 만듭니다.
class RouteQuery(BaseModel):
    """
    사용자 질문에 대해 어떤 카테고리에 해당하는지(휴가, 시간표, 법령) 구조화하여 반환합니다.
    """
    category: Literal["vacation", "timetable", "legal"] = Field(
        ...,
        description="Given a user question, choose which category among [vacation, timetable, legal]."
    )


def route_question(question: str) -> str:
    """
    ChatUpstage를 통해 질문에 대한 카테고리를 JSON 형태로 추론하고,
    Pydantic 모델(RouteQuery)을 이용해 구조화된 결과를 얻습니다.
    """
    # 시스템 프롬프트: LLM에게 "vacation", "timetable", "legal" 중 하나를 JSON 형태로 반환하도록 지시
    system_prompt = """\
You are an expert router that determines the question category among "vacation", "timetable", or "legal".
Return a JSON object in the format: "category": "vacation", "category": "timetable", or "category": "legal".
No extra keys, no additional explanations. 
"""
    # 메시지 템플릿 구성
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}")
        ]
    )

    # ChatUpstage 인스턴스를 사용하여 라우팅용 답변 생성
    chat = ChatUpstage(temperature=1)
    chain = prompt | chat

    raw_response = chain.invoke({"question": question})

    try:
        data = json.loads(raw_response.content.strip())
        route_result = RouteQuery(**data)
        return route_result.category
    except Exception:
        return "etc"


def main(vector_store):
    st.title("AI 부트캠프 매니저 QA봇")

    # 사용자 질문 입력
    question = st.text_input("질문을 입력하세요", "카드 발급은 어떻게 하나요?")  # 기타
    # 싱글

    if st.button("Get Answer"):
        with st.spinner("카테고리 라우팅 중..."):
            # 1. 질문을 라우팅하여 카테고리 결정
            category = route_question(question)

        st.write(f"**예측된 카테고리:** {category}")

        with st.spinner("답변 생성 중..."):
            # Retrieve similar documents from vector_store
            result = search_vector_store(vector_store, question)
            context_text, attached_files = extract_context_and_files(result)

            if category == "vacation":
                context_text = context_text.replace("휴가", "휴가(leave)")
            elif category == "timetable":
                context_text = context_text.replace("시간표", "시간표(timetable)")

            messages = [
                (
                    "system",
                    (
                        "당신은 학원 QA 봇입니다. 질문자는 \"AI+Lab_7기(Upstage_AI+6기)\"입니다. "
                        "당신의 역할은 학사 정책 및 절차, 휴학 신청 등과 관련된 질문에 답변하는 것입니다. "
                        "제공된 컨텍스트를 철저히 분석하여 모든 관련 세부사항을 추출하세요. 추가 자료를 참조할 때에는 "
                        "명시적으로 다음을 포함해야 합니다:\n"
                        "- 첨부파일은 해당 기수에 적합해야힙니다.\n"
                        "- 첨부파일은 질문과 관련있어야합니다.\n"
                        "- 컨텍스트에 제공된 해당 소스 링크들\n"
                        "컨텍스트에 완전한 정보가 포함되어 있지 않더라도, 관련 첨부 파일들이 있는 경우 사용자가 추가 정보를 위해 해당 문서를 참조하도록 안내하세요.\n"
                        "또한, 가독성을 높이기 위해 답변은 bullet point 형식으로 작성하고, 소스 링크가 항상 포함되도록 하세요.\n"
                        "답변은 반드시 한글로 작성되어야 합니다."
                    )
                ),
                (
                    "system",
                    f"참조해야 하는 컨텍스트는 다음과 같습니다:\n{context_text}"
                ),
                (
                    "system",
                    f"추가 세부 정보가 포함될 수 있는 첨부 파일들은 다음과 같습니다:\n{attached_files}"
                ),
                (
                    "human",
                    f"위의 컨텍스트와 첨부 파일 정보를 사용하여, 다음 질문에 대해 포괄적으로 답변하세요:\n\n{question}"
                ),
            ]

            prompt = ChatPromptTemplate.from_messages(messages)

            # 4. ChatUpstage를 활용한 LLM 응답
            response = get_response(prompt, {"question": question})
            st.subheader("LLM 응답")
            st.write(response.content)


if __name__ == "__main__":
    load_dotenv()
    configure_upstage_api()
    vector_store = load_vector_store_once()
    main(vector_store)
