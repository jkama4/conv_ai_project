from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset

from trl import SFTTrainer

from typing import Self

from . import models, config


# IMPORTANT
# Double check whether it is actually training how to act like a user (!!!!!!)
# IMPORTANT

class AssistantAgent:
    dataset: Dataset
    train_ds: Dataset = config.TRAIN_DS
    validation_ds: Dataset = config.VALIDATION_DS
    test_ds: Dataset = config.TEST_DS

    def __init__(self, cfg: models.UserAgentConfig | None = None) -> None:
        self.cfg = cfg or models.UserAgentConfig()
        self.tokenizer: AutoTokenizer = self.cfg._load_tokenizer()
        self.model: AutoModelForCausalLM = self.cfg._load_model()
        self.trainer: SFTTrainer | None = None

    def _setup_trainer(
        self: Self, 
    ) -> SFTTrainer:
        
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

    def _generate(self, prompt, **kwargs):

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            **kwargs
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
