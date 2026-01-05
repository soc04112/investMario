import json
import re
from datetime import timedelta
from app.agent.date_utils import resolve_date_range
from app.agent.tools_market import MAJOR_SYMBOL_MAP

# 툴 판단 + 보정 로직
def decide_tool(llm, system_prompt, user_message, history):
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message},
    ]
    response = llm.chat(messages=messages)

    # tool_call이 wrapper에서 직접 온 경우 (최우선)
    tool_call = response["message"].get("tool_call")
    if tool_call is not None:
        return tool_call

    # content에서 JSON만 안전하게 추출
    content = response["message"].get("content", "").strip()
    
    # JSON 블록만 추출 
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        parsed = json.loads(content[start:end])
        return parsed.get("tool_call")
    except Exception:
        # JSON 파싱 불가 → 도구 사용 안 함으로 처리
        return None


def normalize_args(tool_name, args, user_message, context):
    start, _ = resolve_date_range(user_message)

    # 어제는?
    if start is None and context.get("last_date") and "어제" in user_message:
        start = context["last_date"] - timedelta(days=1)

    # 날짜
    if tool_name == "get_price_by_date" and start:
        args["date_start"] = start.strftime("%Y-%m-%d")
        context["last_date"] = start

    # SYMBOL (절대 user_message 그대로 넣지 않기)
    if tool_name in ("get_price", "get_price_by_date"):
        if not args.get("symbol"):
            if context.get("last_symbol"):
                args["symbol"] = context["last_symbol"]
            # else: 일부러 안 넣음 → tool 내부 normalize_symbol에게 맡김

        if args.get("symbol"):
            sym = args["symbol"].lower()
            if sym in MAJOR_SYMBOL_MAP:
                context["last_symbol"] = sym
            else:
                context["last_symbol"] = args["symbol"]

    if tool_name == "compare_symbols":
        if not args.get("symbols"):
            tokens = re.findall(r"[가-힣]+|[a-z0-9\-]+", user_message.lower())
            symbols = []

            # 단일 토큰
            for t in tokens:
                if t in MAJOR_SYMBOL_MAP:
                    symbols.append(t)

            # 한글 2단어 결합
            for i in range(len(tokens) - 1):
                combined = f"{tokens[i]} {tokens[i+1]}"
                if combined in MAJOR_SYMBOL_MAP:
                    symbols.append(combined)

            # 🔑 중복 제거 + 순서 유지
            symbols = list(dict.fromkeys(symbols))

            # 🔑 멀티턴 보정 (1개면 last_symbol 추가)
            if len(symbols) == 1 and context.get("last_symbol"):
                if context["last_symbol"] not in symbols:
                    symbols.append(context["last_symbol"])

            if symbols:
                args["symbols"] = symbols