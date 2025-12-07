from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_cpp import Llama

from typing import Self, Dict

class UserAgent:

    def __init__(self: Self, persona: str) -> None:
        self.persona = persona
        self.llm: Llama = Llama.from_pretrained(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", 
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        )
    
    def _call(
        self: Self,
        prompt: str,
    ) -> str:
        response: Dict = self.llm.create_chat_completion(
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        msg: str = (
            response["choices"][0]["message"]["content"]
        )

        return msg