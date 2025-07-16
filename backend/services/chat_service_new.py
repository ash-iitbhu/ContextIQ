from typing import Dict, Any

from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from ..prompts import prompt_context_question
from ..config import GOOGLE_GENAI_MODEL, DB_PATH
from ..db import StateDB


class ChatWorkflow:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=GOOGLE_GENAI_MODEL)
        self.parser = StrOutputParser()
        self.checkpointer = StateDB(db_path=DB_PATH).get_state_memory()
        self.graph = self._build_graph()

    def _build_graph(self):
        def generate(state: MessagesState, config: Dict[str, Any]) -> MessagesState:
            configurable = config.get("configurable", {})
            vectordb = configurable.get("vectordb")

            messages = state.get("messages", [])
            question = next(
                (
                    msg.content
                    for msg in reversed(messages)
                    if isinstance(msg, HumanMessage)
                ),
                None,
            )

            context = ""
            if vectordb and question:
                docs = vectordb.similarity_search(question, k=4)
                context = "\n".join(doc.page_content for doc in docs)

            historical_message = "\n".join(
                f"{msg.type.capitalize()}: {msg.content}" for msg in messages
            )
            print("history", historical_message)
            chain = prompt_context_question | self.llm | self.parser
            answer = chain.invoke(
                {
                    "context": context,
                    "history": historical_message,
                    "question": question,
                }
            )
            print("answer", answer)

            new_messages = messages + [AIMessage(content=answer)]

            print("new_message", new_messages)

            return {"messages": new_messages}

        builder = StateGraph(MessagesState)
        builder.add_node("generate", generate)
        builder.set_entry_point("generate")
        builder.set_finish_point("generate")

        return builder.compile(checkpointer=self.checkpointer)

    def invoke(self, session_id: str, vectordb, user_message: str) -> str:

        print("session_id", session_id)
        config = {"configurable": {"thread_id": session_id, "vectordb": vectordb}}

        input_message = HumanMessage(content=user_message)
        output = self.graph.invoke({"messages": [input_message]}, config)
        print("output", output)
        for msg in reversed(output["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content

        return "Sorry, I couldn't generate a response."


class ChatManager:
    def __init__(self, workflow: ChatWorkflow):
        self.workflow = workflow

    def handle_user_input(self, session_id: str, vectordb, user_message: str) -> str:
        return self.workflow.invoke(session_id, vectordb, user_message)
