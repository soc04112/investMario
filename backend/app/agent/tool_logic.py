import json
import re
from datetime import timedelta
from app.agent.date_utils import resolve_date_range
from app.agent.tools_market import MAJOR_SYMBOL_MAP

# 툴 판단 + 보정 로직
def decide_tool(llm, system_prompt, user_message, history):
    # 전체 히스토리 대신 최신 3~5개 정도만 전달하여 
    # 모델이 "답변 모드"에 빠지는 것을 방지합니다.
    recent_history = history[-3:] if history else []
    
    messages = [
        {"role": "system", "content": system_prompt},
        *recent_history,
        {"role": "user", "content": user_message},
    ]
    response = llm.chat(messages=messages)
    print(f"DEBUG LLM Response: {response}") # LLM이 실제로 뭐라고 대답하는지 확인
    msg = response.get("message", {})

    # 1️⃣ tool_call이 직접 온 경우
    if "tool_call" in msg and msg["tool_call"]:
        return msg["tool_call"]

    # 2️⃣ content 안의 JSON 파싱
    content = msg.get("content", "").strip()

    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        parsed = json.loads(content[start:end])
        return parsed.get("tool_call")
    except Exception:
        return None


def normalize_args(tool_name, args, user_message, context):
    args = args or {}
    start, _ = resolve_date_range(user_message)
    # 인자가 필요 없는 도구들은 바로 반환
    if tool_name in ["get_top_movers", "get_trending_coins", "get_market_snapshot"]:
        return args

    # ======================
    # TERM (용어 검색)
    # ======================
    if tool_name == "search_crypto_term":
        args["query"] = user_message
        return args

    # ======================
    # NEWS
    # ======================
    if tool_name == "get_crypto_news":
        args["query"] = user_message
        if start:
            args["start_date"] = start.strftime("%Y-%m-%d")
        return args

    # ======================
    # 날짜 처리
    # ======================
    if tool_name == "get_price_by_date" and start:
        args["date_start"] = start.strftime("%Y-%m-%d")
        context["last_date"] = start

    # ======================
    # SYMBOL 처리 
    # ======================
    use_last = args.pop("use_last_symbol", False)

    if tool_name in ("get_price", "get_price_by_date", "get_24h_stats", "get_market_cap"):
        tokens = re.findall(r"[가-힣]+|[a-z0-9\-]+", user_message.lower())
        found = None

        # 1. 2단어 결합 먼저 (라이트 코인, 이더리움 클래식 등)
        for i in range(len(tokens) - 1):
            combined = f"{tokens[i]} {tokens[i+1]}"
            if combined in MAJOR_SYMBOL_MAP:
                found = combined
                break

        # 2.  단일 토큰
        if not found:
            for t in tokens:
                if t in MAJOR_SYMBOL_MAP:
                    found = t
                    break

        # 3.  못 찾은 경우 → 에러 상태 반환
        if not found:
            # 'use_last_symbol'이 True이고 이전에 대화한 코인이 있다면 그것을 사용
            if use_last and context.get("last_symbol"):
                found = context["last_symbol"]
            else:
        # 심볼을 못 찾았을 때 무조건 에러가 아니라, 
        # 도구 자체에서 "전체 시장"을 지원한다면 그대로 진행하거나, 
        # 특정 가이드 문구를 보냅니다.
                return {"_error": "missing_symbol"}

        args["symbol"] = found
        context["last_symbol"] = found

    # ======================
    # 비교
    # ======================
    if tool_name == "compare_symbols":
        tokens = re.findall(r"[가-힣]+|[a-z0-9\-]+", user_message.lower())
        symbols = []

        # 1️⃣ 두 단어 조합 먼저 (🔥 핵심)
        for i in range(len(tokens) - 1):
            combined = f"{tokens[i]} {tokens[i+1]}"
            if combined in MAJOR_SYMBOL_MAP:
                symbols.append(combined)

        # 2️⃣ 단일 토큰 (이미 포함된 것 제외)
        for t in tokens:
            if t in MAJOR_SYMBOL_MAP:
                # 이미 조합된 토큰의 일부면 스킵
                if any(t in s for s in symbols):
                    continue
                symbols.append(t)

        # 3️⃣ 중복 제거 + 순서 유지
        symbols = list(dict.fromkeys(symbols))

        # 4️⃣ 멀티턴 보정
        if len(symbols) == 1 and context.get("last_symbol"):
            if context["last_symbol"] not in symbols:
                symbols.append(context["last_symbol"])

        if symbols:
            args["symbols"] = symbols
            context["last_symbol"] = symbols[0]

    return args