import os
import json
import openai
from typing import List
from collections import defaultdict

openai.api_version = "2023-03-15-preview"
openai.api_type = 'azure'
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
model_gpt35 = os.getenv("AZURE_GPT35")

MEMORY = defaultdict(list)


class ChatGPT:
    def __init__(self, system_prompt=""):
        self.system_prompt = system_prompt

    @staticmethod
    def clear_history(session_id: str):
        if session_id in MEMORY:
            MEMORY[session_id].clear()

    def chat(self, query: str, history: List, **kwargs):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        resp = openai.ChatCompletion.create(
            deployment_id=model_gpt35,
            model="gpt-3.5-turbo",
            messages=messages,
            stream=False,
            **kwargs)

        res_msg = resp["choices"][0]["message"]
        if "content" not in res_msg:
            res_msg["content"] = "<未回复>"

        history.append({"role": "user", "content": query})
        history.append(res_msg)
        return res_msg

    def stream_chat(self, query: str, session_id: str, **kwargs):
        for r in self.stream_with_history(query, MEMORY[session_id], **kwargs):
            yield json.dumps({"content": r})
        yield json.dumps({"content": "[FINISHED]"})

    def stream_with_history(self, query: str, history: List, **kwargs):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        resp = openai.ChatCompletion.create(
            deployment_id=model_gpt35,
            messages=messages,
            stream=True,
            **kwargs)

        res_msg = {"role": "", "content": ""}
        for delta in resp:
            delta = delta["choices"][0]["delta"]
            if "role" in delta:
                res_msg["role"] = delta["role"]
            if "content" in delta:
                res_msg["content"] += delta["content"]
                yield delta["content"]

        history.append({"role": "user", "content": query})
        history.append(res_msg)
