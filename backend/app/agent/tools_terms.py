from langchain_community.vectorstores import FAISS
from app.embeddings import get_embeddings
import os

_TERM_DB = None

def get_term_db():
    global _TERM_DB
    if _TERM_DB is None:
        _TERM_DB = FAISS.load_local(
            os.getenv("TERM_DB_PATH", "crypto_term_db"),
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _TERM_DB



def search_crypto_term(query, top_k=3):
    db = get_term_db()
    results = db.similarity_search(query, k=top_k)

    return [
        {
            "term": r.metadata.get("term"),
            "category": r.metadata.get("category"),
            "definition": r.page_content
        }
        for r in results
    ]
