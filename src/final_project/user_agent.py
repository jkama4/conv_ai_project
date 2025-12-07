from llama_cpp import Llama

from typing import Self, Dict, List

class UserAgent:

    def __init__(self: Self, persona: str) -> None:
        self.persona = persona
        self.llm: Llama = Llama.from_pretrained(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", 
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        )
    
    def _call(
        self: Self,
        history: List[Dict],
    ) -> str:
        
        system_msg = {
            "role": "system",
            "content": (
                "You are simulating a user (traveler) with the following personality:\n"
                f"{self.persona}\n\n"
                "Respond ONLY as the traveler. Do not take the role of an assistant."
            )
        }

        messages = [system_msg] + history

        response: Dict = self.llm.create_chat_completion(
            messages=messages
        )
        
        msg: str = (
            response["choices"][0]["message"]["content"]
        ).strip()

        return msg