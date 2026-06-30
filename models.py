from pydantic import BaseModel

class OptimizeRequest(BaseModel):
    """最適化リクエストのバリデーションモデル"""
    target_protein: float
    target_fat: float
    target_carbo: float

class OptimizeResponse(BaseModel):
    """最適化結果のレスポンスモデル"""
    optimized_weights: dict[str, float]
    calculated_nutrients: dict[str, float]