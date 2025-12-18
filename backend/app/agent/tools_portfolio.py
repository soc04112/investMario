from app.api.config.config import SessionLocal, UserInformation, TradingHistory
from datetime import datetime, timedelta

def get_user_profile(userid: str):
    db = SessionLocal()
    try:
        row = (
            db.query(UserInformation)
            .filter(UserInformation.userid == userid)
            .order_by(UserInformation.id.desc())
            .first()
        )

        if not row:
            return {"error": "User not found"}

        result = row.__dict__.copy()
        result.pop("_sa_instance_state", None)

        # API 키는 절대 LLM에 노출 금지
        if "key" in result:
            result["key"] = "ENCRYPTED"

        return result

    finally:
        db.close()

def get_latest_strategy(userid: str, limit: int = 5):
    db = SessionLocal()
    try:
        rows = (
            db.query(TradingHistory)
            .filter(TradingHistory.userid == userid)
            .order_by(TradingHistory.id.desc())
            .limit(limit)
            .all()
        )

        if not rows:
            return {"error": "No strategy history found"}

        results = []
        for r in rows:
            item = r.__dict__.copy()
            item.pop("_sa_instance_state", None)
            results.append(item)

        return results

    finally:
        db.close()


from datetime import timedelta

def get_strategy_by_date(userid: str, start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(TradingHistory).filter(TradingHistory.userid == userid)

        # 날짜 지정이 안되면 오류 처리
        if not start_date:
            return {"error": "start_date is required for date-based queries"}

        # 하루 조회: end_date 자동 생성
        if start_date and not end_date:
            end_date = start_date + timedelta(days=1)

        # 문자열이면 datetime으로 변환 (ISO8601 가정)
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        if end_date is None:
            end_date = start_date + timedelta(days=1)
        elif isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        # 날짜 범위 필터 적용
        query = query.filter(
            TradingHistory.time >= start_date,
            TradingHistory.time < end_date
        ).order_by(TradingHistory.time.asc())

        rows = query.all()

        if not rows:
            return {"error": "No strategy history found in selected date range"}

        results = []
        for r in rows:
            item = r.__dict__.copy()
            item.pop("_sa_instance_state", None)
            results.append(item)

        return results

    finally:
        db.close()


