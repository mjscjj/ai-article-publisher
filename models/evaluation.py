from pydantic import BaseModel

class EvaluationResult(BaseModel):
    total_score: float = 0
    grade: str = 'E'

class EvaluationHistory(BaseModel):
    id: int = 0
