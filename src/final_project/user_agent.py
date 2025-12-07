from llama_cpp import Llama
from typing import Self, List, Dict

from . import constants


class UserAgent:

    def __init__(self: Self, persona: str):
        self.persona = persona

        self.llm = Llama.from_pretrained(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            n_ctx=4096,
            n_gpu_layers=40,
        )

    def _call(
        self: Self,
        history: List[Dict],
    ) -> str:

        system_instruction = {
            "role": "system",
            "content": constants.NICE_USER_PERSONA
        }

        messages = [system_instruction] + history

        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_tokens=200,
            stream=False
        )

        msg = response["choices"][0]["message"]["content"].strip()
        return msg
