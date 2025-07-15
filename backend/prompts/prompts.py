from langchain_core.prompts import PromptTemplate

prompt_context_question = PromptTemplate(
    template="Answer the following based on the context:\nContext:\n{context}\nQuestion: {question}",
    input_variables=["context", "question"],
)
