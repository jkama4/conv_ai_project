from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset

from trl import SFTTrainer

from typing import Self, Dict, List

from . import models, config, utils


class BaseAssistantAgent:
    dataset: Dataset
    train_ds: Dataset = config.TRAIN_DS
    validation_ds: Dataset = config.VALIDATION_DS
    test_ds: Dataset = config.TEST_DS

    def __init__(self: Self, cfg: models.UserAgentConfig | None = None) -> None:
        self.cfg = cfg or models.UserAgentConfig()
        self.tokenizer: AutoTokenizer = self.cfg._load_tokenizer()
        self.model: AutoModelForCausalLM = self.cfg._load_model()
        self.trainer: SFTTrainer | None = None

        self.kb: Dict = utils.get_knowledge_base()

    def _setup_trainer(self: Self) -> SFTTrainer:
        self.trainer = self.cfg._load_trainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_ds=self.train_ds,
            eval_ds=self.validation_ds,
        )

    def _train(self: Self) -> SFTTrainer:
        if self.trainer is None:
            raise RuntimeError("trainer is not initialised")
        return self.trainer.train()

    def _generate(self: Self, messages: List[Dict]) -> str:
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs = self.tokenizer(
            [text],
            return_tensors="pt"
        ).to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=200
        )

        return self.tokenizer.decode(
            generated_ids[0][model_inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        ).strip()

    def _call(self: Self, history: List[Dict]) -> str:
        return self._generate(history)


class RAGAssistantAgent(BaseAssistantAgent):

    def _retrieve(self: Self, user_msg: str, top_k: int = 5) -> List:
        words: List[str] = user_msg.lower().split()
        matches: List[str] = []

        for category in ["hotel", "restaurant"]:
            for name, data in self.kb[category].items():
                all_text: str = ""

                for review in data["reviews"].values():
                    for sentence in review["sentences"].values():
                        all_text += " " + sentence.lower()

                if any(w in all_text for w in words):
                    matches.append((name, category, all_text))

        return matches[:top_k]

    def _format_matches(self: Self, matches: List) -> str:
        if not matches:
            return "No relevant knowledge found."

        formatted = []
        for name, category, text in matches:
            formatted.append(f"{name} ({category}): {text}")

        return "\n".join(formatted)

    def _call(self: Self, history: List[Dict]) -> str:

        last_user_msg = next(
            (m["content"] for m in reversed(history) if m["role"] == "user"),
            ""
        )

        kb_matches = self._retrieve(last_user_msg)
        kb_text = self._format_matches(kb_matches)

        rag_context = {
            "role": "system",
            "content": (
                "Use the following knowledge base entries to answer:\n\n"
                f"{kb_text}"
            )
        }

        full_messages = [rag_context] + history

        return self._generate(full_messages)
