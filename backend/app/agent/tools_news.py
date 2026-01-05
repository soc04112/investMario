from langchain_community.vectorstores import FAISS
from app.embeddings import get_embeddings
import os
from datetime import datetime
from typing import Optional
from datetime import datetime
from email.utils import parsedate_to_datetime

def parse_datetime_safe(dt_str: str) -> datetime | None:
    if not dt_str:
        return None

    # 1️⃣ ISO 8601 시도
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        pass

    # 2️⃣ RFC 2822 시도 (Tue, 16 Dec 2025 ...)
    try:
        return parsedate_to_datetime(dt_str)
    except Exception:
        return None



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


def get_crypto_news(
    query: str,
    top_k: int = 3,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    db = get_news_db()
    results = db.similarity_search(query, k=top_k)

    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    articles = []

    for r in results:
        published = r.metadata.get("published_at")
        if not published:
            continue

        published_dt = parse_datetime_safe(published)
        if not published_dt:
            continue

        if start_dt and published_dt < start_dt:
            continue
        if end_dt and published_dt >= end_dt:
            continue

        articles.append({
            "title": r.metadata.get("title"),
            "url": r.metadata.get("url"),
            "published_at": published,
            "summary": r.page_content
        })

        if len(articles) >= top_k:
            break

    return {
        "query": query,
        "article_count": len(articles),
        "articles": articles
    }