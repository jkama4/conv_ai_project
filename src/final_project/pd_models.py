from pydantic import BaseModel

class LLMAsJudgeFormat(BaseModel):
    task_succes_score: float
    coherence_score: float
    pleasentness_score: float
    prediction_score: float
    explanation: str
    