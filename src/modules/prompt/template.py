from langchain_core.prompts import ChatPromptTemplate


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