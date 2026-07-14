from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.property import ValuationInputSchema
from app.schemas.response import BaseResponseSchema
from app.services.ppcp_service import PPCPService


router = APIRouter(
    prefix="/api/ppcp",
    tags=["PPCP"],
)


@router.post("/estimate", response_model=BaseResponseSchema)
def estimate_ppcp(data: ValuationInputSchema, db: Session = Depends(get_db)):
    """
    API tính giá trị BĐS theo phương pháp chi phí (PPCP):
    giá đất (bảng giá nhà nước) + chi phí xây dựng còn lại.
    """
    try:
        sample = data.model_dump()

        # Đảm bảo các trường cần thiết tồn tại
        if not sample.get("PropertyLocation"):
            raise ValueError("Thiếu thông tin PropertyLocation (Ward, Street)")

        result = PPCPService.calculate_ppcp(sample, db)

        if result is None:
            return BaseResponseSchema(
                success=False,
                data={"message": "Không tìm thấy dữ liệu bảng giá đất cho khu vực này"},
            )

        return BaseResponseSchema(success=True, data=result)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán PPCP: {str(e)}")
