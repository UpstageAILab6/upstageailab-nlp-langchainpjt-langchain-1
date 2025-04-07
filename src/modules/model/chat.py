from typing import Any

from langchain_upstage import ChatUpstage

def get_response(prompt, context: Any):
    """
    ChatUpstage 인스턴스를 이용하여 최종 응답을 받아옵니다.
    """
    chat = ChatUpstage(model="solar-pro", temperature=0.7)
    chain = prompt | chat
    response = chain.invoke(context)
    return response