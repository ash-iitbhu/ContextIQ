from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from ..config import GOOGLE_GENAI_MODEL
from ..prompts import prompt_context_question


def get_context(vectordb, request):
    docs = vectordb.similarity_search(request.message, k=4)
    context = "\n".join([doc.page_content for doc in docs])
    return context


def get_answer(context, request):
    llm = ChatGoogleGenerativeAI(model = GOOGLE_GENAI_MODEL)
    prompt = prompt_context_question
    parser = StrOutputParser()
    chain = prompt | llm | parser
    answer = chain.invoke({"context": context, "question": request.message})
    return answer