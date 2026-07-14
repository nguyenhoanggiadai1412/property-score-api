from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.schemas.property import ValuationInputSchema

class BaseResponseSchema(BaseModel):
    success: bool = True
    data: Any

class TargetAssetValuationSchema(BaseModel):
    PropertyId: str
    f_score: float

class ComparableAssetValuationSchema(BaseModel):
    Comparable_id: str
    price: Optional[float]
    f_score: float
    P_tsmt: Optional[int]

class ComparePriceResponseSchema(BaseModel):
    target_asset: TargetAssetValuationSchema
    ComparableAssets: List[ComparableAssetValuationSchema]

class BenchmarkDetailSchema(BaseModel):
    average: int
    median: int
    min: float
    max: float
    range: float
    n_samples: int

class BenchmarkResponseSchema(ValuationInputSchema):
    benchmark: Optional[BenchmarkDetailSchema] = None

class ComponentScoreDetailSchema(BaseModel):
    score: float
    weight: str
    n: Optional[int] = None
    avg_distance_m: Optional[float] = None
    avg_days: Optional[float] = None
    spread_pct: Optional[float] = None

class ComponentScoresSchema(BaseModel):
    so_luong_tsss: ComponentScoreDetailSchema
    khoang_cach: ComponentScoreDetailSchema
    thoi_gian: ComponentScoreDetailSchema
    nguon_du_lieu: ComponentScoreDetailSchema
    bien_gia: ComponentScoreDetailSchema

class ConfidenceResponseSchema(BaseModel):
    PropertyId: Optional[str]
    overall_score: float
    grade: str
    meaning: str
    component_scores: ComponentScoresSchema
    warnings: List[str]
