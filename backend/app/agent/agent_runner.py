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


