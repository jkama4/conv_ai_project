import os

from openai import OpenAI

from typing import Self, List, Dict

from . import constants

OPENAI_CLIENT: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

class UserAgent:

    def __init__(self: Self, persona: str = "nice"):
        self.model_name = "Qwen/Qwen2.5-7B"
        self.persona = persona

    def _call(self: Self, history: List[Dict]):
        
        response = OPENAI_CLIENT.responses.create(
            model="gpt-5-nano",
            input=(
                f"{constants.ANNOYING_USER_PERSONA if self.persona == "annoying" else constants.NICE_USER_PERSONA}\n\n"
                "This is the conversation so far:\n\n"
                f"{history}"
                "It is your task to respond accordingly to the assistant's final message."
                "Don\'t let the conversation go on for too long, and try to get to the point."
                "Also, don't make your responses too long. Keep your responses around 2-3 sentences."
                "Don't use excessive amounts of text for a simple task like this."
                f"{constants.ANNOYING_INSTRUCTION if self.persona == "annoying" else constants.NICE_INSTRUCTION}"
            )
        )

        return response.output_text