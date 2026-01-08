from app.api.config.config import SessionLocal, UserInformation, TradingHistory
from app.services.upbit_api import exchange_information
from datetime import datetime, timedelta

def get_user_profile(userid: str):
    """
    사용자의 기본 프로필 및 설정 정보를 가져옵니다. (최신 JSON 구조 반영)
    """
    db = SessionLocal()
    try:
        row = db.query(UserInformation).filter(UserInformation.userid == userid).first()
        if not row:
            return {"error": "User not found"}

        # 수정된 DB 구조: userinfo, usercustom 딕셔너리에서 데이터 추출
        user_data = {
            "userid": row.userid,
            "username": row.userinfo.get('username') if row.userinfo else None,
            "usemodel": row.userinfo.get('usemodel') if row.userinfo else None,
            "exchange": row.usercustom.get('exchange') if row.usercustom else None,
            "ticker": row.usercustom.get('ticker') if row.usercustom else [],
            "api_key_status": "ENCRYPTED" # LLM 보안을 위해 문자열 처리
        }
        return user_data
    finally:
        db.close()

def get_latest_strategy(userid: str, limit: int = 5):
    """
    사용자의 최근 거래 전략 히스토리를 가져옵니다.
    """
    db = SessionLocal()
    try:
        # TradingHistory 구조에 맞춰 최신순 정렬 및 데이터 추출
        rows = (
            db.query(TradingHistory)
            .filter(TradingHistory.userid == userid)
            .order_by(TradingHistory.time.desc())
            .limit(limit)
            .all()
        )

        if not rows:
            return {"error": "No strategy history found"}

        results = []
        for r in rows:
            results.append({
                "time": r.time.isoformat(),
                "position": r.position,
                "why": r.why
            })
        return results
    finally:
        db.close()

def get_strategy_by_date(userid: str, start_date=None, end_date=None):
    """
    특정 날짜 범위의 거래 전략 기록을 가져옵니다.
    """
    db = SessionLocal()
    try:
        # 입력값이 문자열일 경우 datetime 객체로 변환
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', ''))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', ''))

        if not start_date:
            return {"error": "start_date is required"}
        
        if not end_date:
            end_date = start_date + timedelta(days=1)

        query = db.query(TradingHistory).filter(
            TradingHistory.userid == userid,
            TradingHistory.time >= start_date,
            TradingHistory.time < end_date
        ).order_by(TradingHistory.time.asc())

        rows = query.all()
        if not rows:
            return {"error": "No data found for the given range"}

        return [{"time": r.time.isoformat(), "position": r.position, "why": r.why} for r in rows]
    finally:
        db.close()