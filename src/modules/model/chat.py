from langchain_upstage import ChatUpstage

def get_response(prompt, context: str):
    """
    ChatUpstage 인스턴스를 이용하여 최종 응답을 받아옵니다.
    """
    chat = ChatUpstage()
    chain = prompt | chat
    response = chain.invoke({"context": context})
    return response