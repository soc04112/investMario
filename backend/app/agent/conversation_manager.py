import json

class ConversationManager:
    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self.history = []

    def build_messages(self):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        return messages

    def add_user(self, content: str):
        self.history.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.history.append({"role": "assistant", "content": content})

    def chat(self, user_message: str, tools=None):
        self.add_user(user_message)

        response = self.llm.chat(
            messages=self.build_messages(),
            tools=tools,
            tool_choice="auto"
        )

        msg = response["message"]

        # tool call
        if "tool_call" in msg:
            return {"type": "tool", "tool_call": msg["tool_call"]}

        # normal answer
        self.add_assistant(msg["content"])
        return {"type": "message", "content": msg["content"]}

    def respond_with_tool_result(self, tool_result: dict):
        tool_message = json.dumps(tool_result, ensure_ascii=False)

        self.history.append({
            "role": "user",
            "content": f"<tool_response>{tool_message}</tool_response>"
        })

        response = self.llm.chat(
            messages=self.build_messages(),
            tool_choice="none"
        )

        self.add_assistant(response["message"]["content"])
        return response["message"]["content"]
