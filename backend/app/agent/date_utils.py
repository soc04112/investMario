from datetime import datetime, timedelta, timezone
import re

KST = timezone(timedelta(hours=9))

def resolve_date_range(text: str):
    now = datetime.now(KST)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1️⃣ YYYY년 MM월 DD일 (최우선)
    m = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text)
    if m:
        y, mo, d = map(int, m.groups())
        start = datetime(y, mo, d, tzinfo=KST)
        end = start + timedelta(days=1)

    # 2️⃣ 상대 날짜
    elif "그제" in text:
        start = today - timedelta(days=2)
        end = start + timedelta(days=1)

    elif "어제" in text:
        start = today - timedelta(days=1)
        end = today

    elif "오늘" in text:
        start = today
        end = today + timedelta(days=1)

    elif m := re.search(r"(\d+)\s*일\s*전", text):
        days = int(m.group(1))
        start = today - timedelta(days=days)
        end = start + timedelta(days=1)

    else:
        return None, None

    # 🚫 미래 차단
    if start >= today + timedelta(days=1):
        return "FUTURE", None

    return start, end

# @dataclass
# class ConversationContext:
#     last_intent: Optional[str] = None
#     last_symbol: Optional[str] = None
#     last_date_start: Optional[datetime] = None
#     last_date_end: Optional[datetime] = None


