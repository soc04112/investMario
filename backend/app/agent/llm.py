from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLM:
    def chat(self, messages, tools=None, tool_choice="auto"):
        # ✅ tools가 있을 때만 tool_choice 전달
        kwargs = {
            "model": "gpt-4o-mini",
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        response = client.chat.completions.create(**kwargs)

        msg = response.choices[0].message

        # ✅ tool call 안전 처리
        if getattr(msg, "tool_calls", None):
            tool_call = msg.tool_calls[0]
            return {
                "message": {
                    "tool_call": {
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    }
                }
            }

        # ✅ 일반 답변
        return {
            "message": {
                "content": msg.content or ""
            }
        }

llm = LLM()
