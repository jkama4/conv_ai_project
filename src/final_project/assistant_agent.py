from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset
from peft import PeftModel


from pathlib import Path

from trl import SFTTrainer

from typing import Self, Dict, List, Tuple, Union

from . import data_sets, models, config, utils, constants


class BaseAssistantAgent:
    """
    The Base Assistant Agent, only using the fine-tuned model
    """

    dataset: Dataset
    train_ds: Dataset = data_sets.TRAIN_DS
    validation_ds: Dataset = data_sets.VALIDATION_DS
    test_ds: Dataset = data_sets.TEST_DS

    def __init__(self: Self) -> None:
        self.cfg = models.AssistantAgentConfig()
        self.tokenizer: AutoTokenizer = self.cfg._load_tokenizer() # tokenizer; prepares input for a model
        self.model: AutoModelForCausalLM = self.cfg._setup_peft_model() # model; the actual fine-tuned model
        self.trainer: SFTTrainer | None = None # trainer; used to run training

        self.kb: Dict = utils.get_knowledge_base()

    def _setup_trainer(self: Self) -> SFTTrainer:
        self.trainer = self.cfg._load_trainer( # loads the existing trainer
            model=self.model,
            tokenizer=self.tokenizer,
            train_ds=self.train_ds,
            eval_ds=self.validation_ds,
        )

    def _train(self: Self) -> SFTTrainer:
        """
        Trains the trainer

        :return: trained trainer
        :rtype: SFTTrainer
        """
        if self.trainer is None:
            raise RuntimeError("trainer is not initialised")
        return self.trainer.train()

    def _generate(self: Self, history: List[Dict]) -> str:
        """
        Generate a response, given some history

        :(param) history: history of a conversation
        :return: the final respons of the model
        :rtype: str
        """
        text = self.tokenizer.apply_chat_template(
            history,
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
    
    @classmethod
    def _load_finetuned(
        cls,
        model_path: Path = Path(__file__).parent / "outputs"
    ) -> Tuple["BaseAssistantAgent", AutoTokenizer]:
        """
        Loads the fine-tuned model
        
        :(param) cls: The BaseAssistantAgent class
        :(param) model_path: path to the fine-tuned model
        :return: returns the agent and the tokenizer
        :rtype: Tuple[BaseAssistantAgent, AutoTokenizer]
        """

        agent = cls()
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        base_model_name = agent.cfg.qwen_model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map="auto",
            dtype="auto"
        )

        model = PeftModel.from_pretrained(base_model, model_path)

        agent.tokenizer = tokenizer
        agent.model = model

        return agent, tokenizer


class RAGAssistantAgent(BaseAssistantAgent):
    """
    Enhanced version of the BaseAssistantAgent, making use of lexical 
    based keyword search (not real RAG, use to simplify naming)
    """

    def _retrieve(self: Self, user_msg: str, top_k: int = 5) -> List:
        """
        Retrieves, given the user message, the data entries that match the top 5 most similar data entries
        
        :(param) user_msg: the message of the user (traveler)
        :(param) top_k: top 5 matches 
        :return: a list of reviews that relate to the content
        :rtype: List
        """
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
        """
        Formats the matches found in the knowledge base accordingly

        :(param) matches: list of reviews that relate to the content
        :return: returns a formatted version of the matches found
        :rtype: str
        """
        if not matches:
            return "No relevant knowledge found."

        formatted = []
        for name, category, text in matches:
            formatted.append(f"{name} ({category}): {text}")

        return "\n".join(formatted)

    def _call(self: Self, history: List[Dict]) -> str:
        """
        Calls the agent given some history to respond to
        
        :(param) history: a list of rev
        :return: the generated response of the model
        :rtype: str
        """

        last_user_msg = next(
            (m["content"] for m in reversed(history) if m["role"] == "user"),
            ""
        )

        # matches found in the knowledge base, which are then formatted
        kb_matches = self._retrieve(last_user_msg)
        kb_text = self._format_matches(kb_matches)

        # the context found in the knowledge base, formatted in the way the model takes in messages
        rag_context = {
            "role": "system",
            "content": (
                "Use the following knowledge base entries to answer:\n\n"
                f"{kb_text}"
            )
        }

        # the full history; context from the knowledge base together with the existing history of the conversation
        full_history = [rag_context] + history

        return self._generate(full_history)