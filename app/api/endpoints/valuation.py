from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.property import ValuationInputSchema
from app.schemas.response import BaseResponseSchema, BenchmarkResponseSchema
from app.services.valuation_service import ValuationService

router = APIRouter(
    prefix="/api/ppss",
    tags=["PPSS"]
)

@router.post("/compare-price", response_model=BaseResponseSchema)
def get_compare_price(data: ValuationInputSchema, db: Session = Depends(get_db)):
    """
    API tính toán điều chỉnh đơn giá định giá giữa tài sản mục tiêu và các TSSS dựa trên các rule được load động từ DB.
    """
    try:
        result = ValuationService.calculate_compare_price(data, db)
        return BaseResponseSchema(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán: {str(e)}")

@router.post("/benchmark", response_model=BenchmarkResponseSchema)
def get_benchmark(data: ValuationInputSchema):
    """
    API tính toán benchmark thống kê đơn giá tài sản so sánh.
    """
    try:
        result = ValuationService.calculate_benchmark(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán: {str(e)}")
