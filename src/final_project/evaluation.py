import os

from typing import Dict, Tuple, List

from openai import OpenAI
from sacrebleu.metrics import BLEU
from rouge import Rouge

from torchmetrics.text.bert import BERTScore

from . import constants
from .pd_models import LLMAsJudgeFormat


def gather_objective_data(
    convo_data: Dict
) -> Dict:
        
    convo: List[Dict] = convo_data["conversation"]

    predicted: str = convo_data["metadata"]["predicted"]
    ground_truth: str = convo_data["metadata"]["ground_truth"]

    for idx, s in enumerate(convo):
        if s["content"] == predicted:
            completion = convo[idx:]

    assistant_tokens, user_tokens = calc_tokens(
        completion=completion
    )

    bleu, rouge, bertscore = eval_answers(
        pred=predicted,
        ref=ground_truth,
    )

    return {
        "total_turns": len(convo),
        "turns_history_only": len(convo) - len(completion),
        "turns_completion_only": len(completion),
        "assistant_tokens": assistant_tokens,
        "user_tokens": user_tokens,
        "bleu_score": bleu,
        "rouge_score": rouge,
        "bertscore": bertscore,
        "user_persona": convo_data["metadata"]["persona"],
        "assistant_class": convo_data["metadata"]["assistant_type"]
    }


def compute_bleu(
    pred: str,
    ref: str,
) -> float:
    bleu_scorer: BLEU = BLEU(effective_order=True)

    score = bleu_scorer.sentence_score(
        hypothesis=pred,
        references=[ref]
    )
    
    return score.score / 100


def compute_rouge(
    pred: str,
    ref: str,
) -> float:
    rouge_scorer = Rouge()

    score = rouge_scorer.get_scores(
        hyps=pred,
        refs=ref,
    )

    return score[0]["rouge-l"]["f"]


def compute_bertscore(
    pred: str,
    ref: str,
) -> float:
    
    bertscore = BERTScore()

    score = bertscore(pred, ref)

    return score


def eval_answers(
    pred: str,
    ref: str,
) -> Tuple[float]:
    
    bleu = compute_bleu(pred=pred, ref=ref)
    rouge = compute_rouge(pred=pred, ref=ref)
    bertscore = compute_bertscore(pred=pred, ref=ref)

    return bleu, rouge, bertscore


def calc_tokens(
    completion: List[Dict]
) -> Tuple[int, int]:
    
    assistant_texts, user_texts = [], []

    for turn in completion:
        if turn["role"] == "assistant":
            assistant_texts.append(turn["content"])
        else:
            user_texts.append(turn["content"])

    assistant_texts = " ".join(assistant_texts)
    user_texts = " ".join(user_texts)

    return len(assistant_texts), len(user_texts)


def gather_subjective_data(
    convo_data: Dict
) -> Dict:
    
    convo: List[Dict] = convo_data["conversation"]
    pred_sentence: str = convo_data["metadata"]["predicted"]
    gt_sentence: str = convo_data["metadata"]["ground_truth"]
    
    client: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": (
                    f"{constants.LLM_JUDGE_INSTRUCTION}"
                    "The following example conversation " 
                    "is an example of a conversation with " ""
                    "a high task success score (0.8 - 1.0): \n\n"
                    f"{constants.HIGH_SUCCESS_RATE_EXAMPLE}"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Evaluate the following conversation: {convo}"
                    f"PREDICTED SENTENCE: {pred_sentence}"
                    f"GROUND TRUTH: {gt_sentence}"
                )
            },
        ],
        text_format=LLMAsJudgeFormat,
    )

    data: LLMAsJudgeFormat = response.output_parsed

    return {
        "task_success_score": data.task_succes_score,
        "coherence_score": data.coherence_score,
        "pleasentness_score": data.pleasentness_score,
        "prediction_score": data.prediction_score,
        "explanation": data.explanation,
    }