from datetime import datetime, timedelta, timezone
import re

KST = timezone(timedelta(hours=9))

def resolve_date_range(text: str):
    now = datetime.now(KST)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 오늘
    if "오늘" in text:
        start = today
        end = today + timedelta(days=1)

    # 어제
    elif "어제" in text:
        start = today - timedelta(days=1)
        end = today

    # 그제
    elif "그제" in text:
        start = today - timedelta(days=2)
        end = today - timedelta(days=1)

    # N일 전 (3일 전, 5일 전 등)
    elif m := re.search(r"(\d+)\s*일\s*전", text):
        days = int(m.group(1))
        start = today - timedelta(days=days)
        end = start + timedelta(days=1)

    # 일주일 전
    elif "일주일 전" in text:
        start = today - timedelta(days=7)
        end = start + timedelta(days=1)

    # 최근 N일
    elif m := re.search(r"최근\s*(\d+)\s*일", text):
        days = int(m.group(1))
        start = today - timedelta(days=days)
        end = today

    # YYYY년 MM월 DD일
    else:
        m = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text)
        if not m:
            return None, None

        y, mo, d = map(int, m.groups())
        start = datetime(y, mo, d, tzinfo=KST)
        end = start + timedelta(days=1)

    # 🚫 미래 차단
    if start >= today + timedelta(days=1):
        return None, None

    return start, end

# @dataclass
# class ConversationContext:
#     last_intent: Optional[str] = None
#     last_symbol: Optional[str] = None
#     last_date_start: Optional[datetime] = None
#     last_date_end: Optional[datetime] = None


