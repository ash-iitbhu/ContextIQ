from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


async def ingest_data(text):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)
        embedder = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        vectordb = FAISS.from_texts(chunks, embedder)
        return vectordb
    except Exception as e:
        return {"error": f"Embedding or storage error: {str(e)}"}
