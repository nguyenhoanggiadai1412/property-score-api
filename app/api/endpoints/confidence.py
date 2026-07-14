from fastapi import APIRouter, HTTPException
from app.schemas.property import ValuationInputSchema
from app.schemas.response import BaseResponseSchema
from app.services.confidence_service import ConfidenceService

router = APIRouter(
    prefix="/api/confidence",
    tags=["Confidence"]
)

@router.post("/score", response_model=BaseResponseSchema)
def get_confidence_score(data: ValuationInputSchema):
    """
    API tính điểm tin cậy tổng thể (Confidence Score) cho kết quả định giá AVM.
    """
    try:
        result = ConfidenceService.calculate_confidence_score(data)
        return BaseResponseSchema(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán: {str(e)}")
