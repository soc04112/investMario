# Agent Runner (LLM + Tool 연결)
from app.agent.llm import llm
from app.agent.tool_dispatcher import dispatch_tool
from app.agent.prompt import TOOL_SYSTEM_PROMPT, EXPLAIN_SYSTEM_PROMPT
from app.agent.tool_logic import decide_tool, normalize_args
from app.agent.date_utils import resolve_date_range

import json


SESSION_MESSAGES: dict[str, list] = {}
SESSION_CONTEXT: dict[str, dict] = {}

# 멀티턴 상태 함수
def get_session(userid: str):
    history = SESSION_MESSAGES.setdefault(userid, [])
    context = SESSION_CONTEXT.setdefault(userid, {
        "last_symbol": None,
        "last_date": None,
        "last_intent": None,
    })
    return history, context


# ============================
# Main Agent Runner
# ============================

async def run_agent(user_message: str, userid: str):
    history, context = get_session(userid)

    tool_call = decide_tool(llm, TOOL_SYSTEM_PROMPT, user_message, history)

    start, _ = resolve_date_range(user_message)
    # # 🔥 TERM 강제
    # TERM_KEYWORDS = ["용어", "뜻", "뭐야", "의미", "개념", "설명"]
    # if tool_call is None and any(k in user_message for k in TERM_KEYWORDS):
    #     tool_call = {
    #         "name": "search_crypto_term",
    #         "arguments": {}
    #     }

    if tool_call is None:
        if "비교" in user_message:
            tool_call = {"name": "compare_symbols", "arguments": {}}

        # 🔥 날짜가 없을 때만 get_price 허용
        elif "시세" in user_message and start is None:
            tool_call = {"name": "get_price", "arguments": {}}

        # 🔥 날짜가 있으면 과거 조회로 강제
        elif "시세" in user_message and start is not None:
            tool_call = {"name": "get_price_by_date", "arguments": {}}

    # Tool 미사용 → 일반 답변 생성
    if not tool_call:
        messages = [
            {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": user_message},
        ]
        resp = llm.chat(messages=messages)
        answer = resp["message"]["content"].strip()
        if answer.startswith("{"):
            answer = "질문을 이해하지 못했습니다. 다시 말씀해 주세요."

        history += [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ]
        return {"answer": answer, "tool": None}

    # Tool 실행 준비
    tool_name = tool_call["name"]
    args = normalize_args(tool_name, tool_call.get("arguments", {}), user_message, context)
    
    # 핵심: unsupported 처리
    if isinstance(args, dict) and args.get("_error") == "unsupported_symbol":
        answer = "죄송해요. 해당 코인은 아직 지원하지 않아요. 다른 코인을 입력해 주세요."
        history += [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": answer},
        ]
        return {"answer": answer, "tool_used": None}

    # Tool 실행
    tool_result = dispatch_tool(
        tool_call={"name": tool_name, "arguments": args},
        userid=userid,
    )

    # Tool 결과 설명
    messages = [
        {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
    사용자 질문:
    {user_message}

    도구 이름:
    {tool_name}

    도구 실행 결과(JSON):
    {json.dumps(tool_result, ensure_ascii=False)}
    """.strip(),
        },
    ]
    answer = llm.chat(messages=messages)["message"]["content"]

    # 히스토리 저장
    history += [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]

    return {"answer": answer, "tool": tool_name}
