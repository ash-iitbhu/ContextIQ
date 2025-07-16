from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..db.milvus_vector_store import MilvusVectorStore
import uuid


async def ingest_data(text, username, session_id, doc_type, document_name):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)
        embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        embeddings = embedder.embed_documents(chunks)
        doc_ids = [str(uuid.uuid4()) for _ in chunks]
        # Ensure username is a string
        username_str = username if isinstance(username, str) else str(username)
        usernames = [username_str] * len(chunks)
        session_ids = [session_id] * len(chunks)
        doc_types = [doc_type] * len(chunks)
        document_names = [document_name] * len(chunks)
        milvus_store = MilvusVectorStore(dim=len(embeddings[0]))
        milvus_store.insert_documents(
            doc_ids,
            usernames,
            session_ids,
            doc_types,
            document_names,
            chunks,
            embeddings,
        )
        return milvus_store
    except Exception as e:
        return {"error": f"Embedding or storage error: {str(e)}"}
