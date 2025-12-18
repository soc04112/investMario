# Agent Runner (LLM + Tool 연결)
from app.agent.llm import llm
from app.agent.tool_dispatcher import dispatch_tool
from app.agent.schemas import TOOLS_SCHEMA
from app.agent.conversation_manager import ConversationManager
import json

SESSION_MESSAGES: dict[str, list] = {}

async def run_agent(user_message: str, userid: str):

    if userid not in SESSION_MESSAGES:
        SESSION_MESSAGES[userid] = [
            {"role": "system", "content": "You are a crypto trading assistant."}
        ]

    messages = SESSION_MESSAGES[userid]

    messages.append({"role": "user", "content": user_message})

    response = llm.chat(
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )

    msg = response.get("message", {})

    if isinstance(msg, dict) and "tool_call" in msg:
        tool_call = msg["tool_call"]

        try:
            tool_result = dispatch_tool(
                tool_call=tool_call,
                userid=userid
            )
        except Exception as e:
            print("🔥 TOOL ERROR:", e)
            raise

        final_response = llm.chat(
            messages=[
                {"role": "system", "content": "You are a crypto trading assistant."},
                {"role": "assistant", "content": json.dumps(tool_result, ensure_ascii=False)},
                {"role": "user", "content": "위 결과를 사용자에게 자연스럽게 설명해줘."}
            ]
        )

        answer = final_response["message"]["content"]

        messages.append({"role": "assistant", "content": answer})

        return {"answer": answer, "tool": tool_call["name"]}

    # 일반 답변
    content = msg.get("content", "")
    messages.append({"role": "assistant", "content": content})

    return {"answer": content, "tool": None}


# agent_prompt = """
# You are a professional crypto market research AI agent.

# You provide INFORMATION ONLY.
# You must NEVER give investment advice, predictions, or trading recommendations.

# You have access to the following tools and MUST use them according to the rules.

# NEWS TOOL:
# - get_crypto_news → use when question involves events, reasons, incidents, regulations, hacks, policy, ETF, investigations, outages.

# MARKET TOOLS:
# - Price → get_price
# - 24H statistics → get_24h_stats
# - Comparison → compare_symbols
# - Movers → get_top_movers
# - Market ranking → get_market_cap
# - Trending coins → get_trending_coins
# - Market summary → get_market_snapshot

# ECONOMY TERM TOOL:
# - search_crypto_term → use when question asks about financial concepts, economic terms, policies, indicators, theories, macroeconomic definitions.

# PORTFOLIO TOOLS:
# - get_user_profile
# - get_latest_strategy
# - get_strategy_by_date

# Multi-turn memory
# - Always consider previous conversation context
# - Do NOT change topic abruptly unless the user does

# ## OUTPUT RULES
# - Respond in Korean only
# - Never give buy/sell advice
# - Never expose JSON or tool output
# - Keep the tone professional
# - DO NOT answer from memory
# - DO NOT generate a natural language answer first
# - Must use tools 
# """
# # 멀티턴
# SESSION_STORE: dict[str, ConversationManager] = {}


# async def run_agent(user_message: str, userid: str):
#     """
#     Stateful Agent Runner
#     - userid 기준 ConversationManager 유지 (멀티턴)
#     - LLM이 tool 판단
#     - tool 미사용 시 서버가 재요청 (강제)
#     """

#     # 1️⃣ 유저별 ConversationManager 생성
#     if userid not in SESSION_STORE:
#         SESSION_STORE[userid] = ConversationManager(
#             llm=llm,
#             system_prompt=agent_prompt
#         )

#     cm = SESSION_STORE[userid]

#     # 2️⃣ 1차 LLM 호출 (멀티턴 히스토리 포함)
#     result = cm.chat(
#         user_message=user_message,
#         tools=TOOLS_SCHEMA
#     )

#     # 3️⃣ Tool 호출이 나온 경우
#     if result["type"] == "tool":
#         tool_call = result["tool_call"]

#         # 🔧 실제 Tool 실행
#         tool_result = dispatch_tool(
#             tool_call=tool_call,
#             userid=userid
#         )

#         # 4️⃣ Tool 결과 → 자연어 설명 (LLM이 담당)
#         final_answer = cm.respond_with_tool_result(
#             tool_result=tool_result
#         )

#         return {
#             "answer": final_answer,
#             "tool_used": tool_call["name"]
#         }

#     # 4️⃣ ❗ Tool을 안 썼다면 → 서버에서 강제 재요청
#     retry = cm.force_tool_call(
#         original_question=user_message,
#         tools=TOOLS_SCHEMA
#     )

#     if retry and retry["type"] == "tool":
#         tool_call = retry["tool_call"]

#         tool_result = dispatch_tool(
#             tool_call=tool_call,
#             userid=userid
#         )

#         final_answer = cm.respond_with_tool_result(
#             tool_result=tool_result
#         )

#         return {
#             "answer": final_answer,
#             "tool_used": tool_call["name"]
#         }

#     # 5️⃣ 진짜 예외 상황 (정보 제공 불가)
#     return {
#         "answer": result["content"],
#         "tool_used": None
# }
# async def run_agent(user_message: str, userid: str):

    
#     messages = [
#         {
#             "role": "system",
#             "content": agent_prompt
#         },
#         {
#             "role": "user",
#             "content": user_message
#         }
#     ]

#     # 1) LLM 호출
#     response = llm.chat(
#         messages=messages,
#         tools=TOOLS_SCHEMA,
#         tool_choice="auto"
#     )

#     msg = response["message"]

#     # 2) Tool call이 있으면 실행
#     if "tool_call" in msg:
#         tool_call = msg["tool_call"]

#         tool_result = dispatch_tool(
#             tool_call=tool_call,
#             userid=userid
#         )

#         # 3) Tool 결과를 다시 LLM에 보내서 최종 답변 생성
#         followup_messages = messages + [
#             {
#                 "role": "system", 
#                 "content": agent_prompt
#             },
#             {
#                 "role": "assistant",
#                 "content": f"도구 실행 결과입니다:\n{json.dumps(tool_result, ensure_ascii=False)}"
#             },
#             {
#                 "role": "user",
#                 "content": "위 결과를 사용자에게 자연스럽게 설명해줘."
#             }
#         ]

#         final_response = llm.chat(
#             messages=followup_messages
#         )

#         return {
#             "answer": final_response["message"]["content"],
#             "tool": tool_call["name"]
#         }

#     # 4️⃣ Tool 안 쓴 일반 답변
#     return {
#         "answer": msg["content"],
#         "tool": None
#         }