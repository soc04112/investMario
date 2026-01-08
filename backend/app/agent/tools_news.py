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


from langchain_community.vectorstores.utils import DistanceStrategy

def get_crypto_news(
    query: str,
    top_k: int = 3,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_similarity: float = 0.3  # 0.3 이상의 유사도만 허용
):
    db = get_news_db()
    
    # 1. similarity_search_with_relevance_scores 사용
    # 이 메서드는 내부적으로 점수를 0~1 사이의 '유사도'로 정규화해서 반환합니다.
    results_with_scores = db.similarity_search_with_relevance_scores(query, k=top_k * 2)

    start_dt = parse_datetime_safe(start_date) if start_date else None
    end_dt = parse_datetime_safe(end_date) if end_date else None

    articles = []

    for doc, similarity in results_with_scores:
        # 2. 유사도 임계값 체크 (사용자 설정: 0.3)
        if similarity < min_similarity:
            continue

        published = doc.metadata.get("published_at")
        pub_dt = parse_datetime_safe(published)

        # 3. 날짜 필터링 (선택 사항)
        if start_dt and pub_dt and pub_dt < start_dt:
            continue
        if end_dt and pub_dt and pub_dt > end_dt:
            continue

        articles.append({
            "title": doc.metadata.get("title", "제목 없음"),
            "url": doc.metadata.get("url", ""),
            "published_at": published,
            "summary": doc.page_content
        })
        
        if len(articles) >= top_k:
            break

    return {
        "query": query,
        "article_count": len(articles),
        "articles": articles
    }