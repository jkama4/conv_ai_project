from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, PeftModel, PeftMixedModel
from trl import SFTTrainer, SFTConfig

from datasets import Dataset

from dataclasses import dataclass
from typing import Self, Tuple

from . import utils, config
    

@dataclass
class AssistantAgentConfig:
    qwen_model: str = "Qwen/Qwen3-1.7B"
    r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    bias: str = "none"
    use_rslora: bool = False
    target_modules: Tuple[str] = (
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    )

    def _load_tokenizer(self: Self) -> AutoTokenizer:
        return AutoTokenizer.from_pretrained(self.qwen_model, use_fast=True)
    
    def _load_model(self: Self) -> PeftModel:
        base = AutoModelForCausalLM.from_pretrained(
            self.qwen_model,
            dtype="auto",
            device_map="auto",
        )

        peft_cfg = LoraConfig(
            r=self.r,
            lora_alpha=self.lora_alpha,
            lora_dropout=self.lora_dropout,
            bias=self.bias,
            use_rslora=self.use_rslora,
            target_modules=self.target_modules,
        )

        return get_peft_model(base, peft_cfg)
    
    def _load_sft_config(self: Self):
        return SFTConfig(
            output_dir="outputs",
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            learning_rate=config.ASSISTANT_LR,
            warmup_ratio=0.1,
            num_train_epochs=config.ASSISTANT_NUM_TRAIN_EPOCHS,
            logging_steps=10,
            lr_scheduler_type="linear",
            weight_decay=0.01,
            max_length=1024,
            optim="adamw_torch_fused",
            fp16=not utils.pick_bf16(),
            bf16=utils.pick_bf16(),
            packing=False,
            dataset_num_proc=2,
            report_to="none",
            seed=3407,
        )

    def _load_trainer(
        self: Self, 
        model: PeftModel, 
        tokenizer: AutoTokenizer, 
        train_ds: Dataset,
        eval_ds: Dataset | None = None,
    ) -> SFTTrainer:
        
        args: SFTConfig = self._load_sft_config()

        return SFTTrainer(
            model=model,
            args=args,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            processing_class=tokenizer,
        )