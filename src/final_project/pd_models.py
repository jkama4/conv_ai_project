from pydantic import BaseModel

class LLMAsJudgeFormat(BaseModel):
    """
    Format provided to LLM as a judge
    """
    task_succes_score: float
    coherence_score: float
    pleasentness_score: float
    prediction_score: float
    explanation: str
    