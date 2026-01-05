from openai import OpenAI
import json
import os
import requests
import re


VLLM_URL = os.getenv("VLLM_URL")

TOOL_CALL_PATTERN = re.compile(
    r"<tool_call>\s*(\{.*?\})\s*</tool_call>",
    re.DOTALL
)

class LLM:
    def chat(self, messages, tools=None, tool_choice="auto"):
        payload = {
            "model": "qwen-crypto",
            "messages": messages,
            "temperature": 0,
            "max_tokens": 512,
        }

        resp = requests.post(
            VLLM_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )
        resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()

        # ✅ 1. tool_call 태그 먼저 검사 (훈련 분포 그대로)
        match = TOOL_CALL_PATTERN.search(content)
        if match:
            try:
                tool_call = json.loads(match.group(1))
                return {
                    "message": {
                        "content": "",
                        "tool_call": tool_call
                    }
                }
            except json.JSONDecodeError:
                pass  # fallthrough

        # ✅ 2. 일반 텍스트 응답
        return {
            "message": {
                "content": content,
                "tool_call": None
            }
        }
llm = LLM()






# gpt-4o-mini
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# class LLM:
#     def chat(self, messages, tools=None, tool_choice="auto"):
#         # ✅ tools가 있을 때만 tool_choice 전달
#         kwargs = {
#             "model": "gpt-4o-mini",
#             "messages": messages,
#         }

#         if tools:
#             kwargs["tools"] = tools
#             kwargs["tool_choice"] = tool_choice

#         response = client.chat.completions.create(**kwargs)

#         msg = response.choices[0].message

#         # ✅ tool call 안전 처리
#         if getattr(msg, "tool_calls", None):
#             tool_call = msg.tool_calls[0]
#             return {
#                 "message": {
#                     "tool_call": {
#                         "name": tool_call.function.name,
#                         "arguments": json.loads(tool_call.function.arguments)
#                     }
#                 }
#             }

#         # ✅ 일반 답변
#         return {
#             "message": {
#                 "content": msg.content or ""
#             }
#         }

# llm = LLM()
