import json
import re
from datetime import timedelta
from app.agent.date_utils import resolve_date_range
from app.agent.tools_market import MAJOR_SYMBOL_MAP


# =========================
# 한국어 조사 제거 유틸
# =========================
KOREAN_PARTICLES = (
    "과", "와", "랑", "하고",
    "은", "는", "이", "가",
    "을", "를",
    "의", "도", "만", "에서", "으로", "로"
)

def strip_particles(text: str) -> str:
    """
    도지코인과 → 도지코인
    리플을 → 리플
    """
    for p in KOREAN_PARTICLES:
        if text.endswith(p):
            return text[:-len(p)]
    return text


def tokenize(user_message: str) -> list[str]:
    """
    1. 한글/영문 토큰 분리
    2. 조사 제거
    """
    raw_tokens = re.findall(r"[가-힣]+|[a-z0-9\-]+", user_message.lower())
    return [strip_particles(t) for t in raw_tokens]


# =========================
# 툴 판단 로직
# =========================
def decide_tool(llm, system_prompt, user_message, history):
    # 최근 히스토리만 사용 (답변 모드 방지)
    recent_history = history[-3:] if history else []

    messages = [
        {"role": "system", "content": system_prompt},
        *recent_history,
        {"role": "user", "content": user_message},
    ]

    response = llm.chat(messages=messages)
    print(f"DEBUG LLM Response: {response}")

    msg = response.get("message", {})

    # 1️⃣ tool_call 직접 반환
    if msg.get("tool_call"):
        return msg["tool_call"]

    # 2️⃣ content 안 JSON 파싱 시도
    content = msg.get("content", "").strip()
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        parsed = json.loads(content[start:end])
        return parsed.get("tool_call")
    except Exception:
        return None


# =========================
# 인자 보정 로직
# =========================
def normalize_args(tool_name, args, user_message, context):
    args = args or {}
    start, _ = resolve_date_range(user_message)
    tokens = tokenize(user_message)

    # ---------------------
    # 인자 필요 없는 툴
    # ---------------------
    if tool_name in [
        "get_top_movers",
        "get_trending_coins",
        "get_market_snapshot",
        "get_user_profile",
        "get_latest_strategy",
    ]:
        return args

    # ---------------------
    # TERM
    # ---------------------
    if tool_name == "search_crypto_term":
        args["query"] = user_message
        return args

    # ---------------------
    # NEWS
    # ---------------------
    if tool_name == "get_crypto_news":
        args["query"] = user_message
        if start:
            args["start_date"] = start.strftime("%Y-%m-%d")
        return args

    # ---------------------
    # 날짜 처리
    # ---------------------
    if tool_name == "get_price_by_date" and start:
        args["date_start"] = start.strftime("%Y-%m-%d")
        context["last_date"] = start

    # ---------------------
    # SYMBOL (단일)
    # ---------------------
    use_last = args.pop("use_last_symbol", False)

    if tool_name in (
        "get_price",
        "get_price_by_date",
        "get_24h_stats",
        "get_market_cap",
    ):
        found = None

        # 1️⃣ 두 단어 결합
        for i in range(len(tokens) - 1):
            combined = f"{tokens[i]} {tokens[i + 1]}"
            if combined in MAJOR_SYMBOL_MAP:
                found = combined
                break

        # 2️⃣ 단일 토큰
        if not found:
            for t in tokens:
                if t in MAJOR_SYMBOL_MAP:
                    found = t
                    break

        # 3️⃣ 멀티턴 보정
        if not found:
            if use_last and context.get("last_symbol"):
                found = context["last_symbol"]
            else:
                return {"_error": "missing_symbol"}

        args["symbol"] = found
        context["last_symbol"] = found
        return args

    # ---------------------
    # 비교 (🔥 핵심)
    # ---------------------
    if tool_name == "compare_symbols":
        symbols = []

        # 1️⃣ 두 단어 조합
        for i in range(len(tokens) - 1):
            combined = f"{tokens[i]} {tokens[i + 1]}"
            if combined in MAJOR_SYMBOL_MAP:
                symbols.append(combined)

        # 2️⃣ 단일 토큰
        for t in tokens:
            if t in MAJOR_SYMBOL_MAP and not any(t in s for s in symbols):
                symbols.append(t)

        # 3️⃣ 중복 제거
        symbols = list(dict.fromkeys(symbols))

        # 4️⃣ 멀티턴 보정
        if len(symbols) == 1 and context.get("last_symbol"):
            if context["last_symbol"] not in symbols:
                symbols.append(context["last_symbol"])

        if not symbols:
            return {"_error": "missing_symbol"}

        args["symbols"] = symbols
        context["last_symbol"] = symbols[0]
        return args

    return args
