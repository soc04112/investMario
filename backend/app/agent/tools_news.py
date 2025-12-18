from langchain_community.vectorstores import FAISS
from app.embeddings import get_embeddings
import os

_NEWS_DB = None

def get_news_db():
    global _NEWS_DB
    if _NEWS_DB is None:
        _NEWS_DB = FAISS.load_local(
            os.getenv("NEWS_DB_PATH", "crypto_news_db"),
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _NEWS_DB


def get_crypto_news(query, top_k=5):
    db = get_news_db()
    results = db.similarity_search(query, k=top_k)

    return [
        {
            "title": r.metadata["title"],
            "url": r.metadata["url"],
            "published_at": r.metadata["published_at"],
            "summary": r.page_content
        }
        for r in results
    ]
