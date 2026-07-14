"""
PPCP Service — Phương pháp chi phí (Cost Approach)

Tính giá trị bất động sản = giá đất (tra bảng giá nhà nước) + chi phí xây dựng còn lại.
- Bảng giá đất (đơn giá): query `bang_gia_dat`
- Khấu hao: query `depreciation_rate`
Kết nối DB dùng engine/session chung từ core/database.
"""

from __future__ import annotations

import datetime
from typing import Optional, Dict, Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.ppcp import BangGiaDat, ConstructionUnitPrice, DepreciationRate
from app.utils.helper import normalize_text

class PPCPService:
    """
    Phương pháp chi phí (PPCP): tính giá trị BĐS dựa trên bảng giá đất
    nhà nước (bang_gia_dat) + chi phí xây dựng còn lại.
    """

    DEFAULT_DEPRECIATION_RATE = 0.0500          # Cấp 4
    DEFAULT_CONSTRUCTION_UNIT_PRICE = 3_250_000  # Cấp 4 - Nhà đơn giản

    # ------------------------------------------------------------------
    # Vị trí (VT) — xác định cột giá trên bảng giá đất nhà nước
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_vt(road_access_type: str, road_width: float) -> str:
        """Rule xác định vị trí (VT1–VT5) theo đơn giá nhà nước."""
        if road_access_type == "Mặt tiền":
            return "VT1"
        if road_width >= 5:
            return "VT2"
        if road_width >= 3:
            return "VT3"
        if road_width >= 2:
            return "VT4"
        return "VT5"

    # ------------------------------------------------------------------
    # Đơn giá đất — tra bảng bang_gia_dat qua ORM
    # ------------------------------------------------------------------

    @staticmethod
    def _query_land_price(
        db: Session,
        ward: str,
        street: str,
    ) -> pd.DataFrame:
        """
        Query bảng `bang_gia_dat` — giữ nguyên logic SQL gốc, dùng ORM.
        """
        rows = (
            db.query(BangGiaDat)
            .filter(
                BangGiaDat.khu_vuc.ilike(f"%{ward}%"),
                BangGiaDat.duong.ilike(f"%{street}%"),
                BangGiaDat.loai.ilike("Đất ở"),
            )
            .all()
        )

        if not rows:
            return pd.DataFrame()

        records = [
            {
                "STT": r.STT,
                "khu_vuc": r.khu_vuc,
                "duong": r.duong,
                "doan": r.doan,
                "VT1": r.VT1,
                "VT2": r.VT2,
                "VT3": r.VT3,
                "VT4": r.VT4,
                "VT5": r.VT5,
                "loai": r.loai,
            }
            for r in rows
        ]
        return pd.DataFrame(records)

    @classmethod
    def _get_unit_price(
        cls,
        row: pd.Series,
        road_access_type: str,
        road_width: float,
    ) -> Optional[Dict[str, Any]]:
        """Fallback ngược về VT gần nhất có giá."""
        target_vt = cls._determine_vt(road_access_type, road_width)
        vt_order = ["VT1", "VT2", "VT3", "VT4", "VT5"]
        idx = vt_order.index(target_vt)

        for i in range(idx, -1, -1):
            vt = vt_order[i]
            value = row[vt]
            if value is not None and not pd.isna(value) and value != 0:
                return {
                    "target_vt": target_vt,
                    "used_vt": vt,
                    "unit_price": float(value),
                }
        return None

    @classmethod
    def _estimate_land_value(
        cls,
        df: pd.DataFrame,
        sample: dict,
    ) -> Optional[Dict[str, Any]]:
        """Tính giá đất = đơn giá × diện tích từ kết quả query bảng giá."""
        if len(df) == 0:
            return None

        row = df.iloc[0]
        result = cls._get_unit_price(row, sample["RoadAccessType"], sample["RoadWidth"])
        if result is None:
            return None

        result["land_value"] = result["unit_price"] * sample["land_area"]
        return result

    # ------------------------------------------------------------------
    # Đơn giá xây dựng — tra bảng construction_unit_price trên DB
    # ------------------------------------------------------------------

    @staticmethod
    def _get_construction_unit_price(
        db: Session,
        building_grade: str,
        property_type: str,
    ) -> float:
        """
        Tra bảng đơn giá xây dựng theo (building_grade, property_type).
        Nếu không khớp -> fallback Cấp 4 - Nhà đơn giản.
        """
        row = (
            db.query(ConstructionUnitPrice.unit_price)
            .filter(
                ConstructionUnitPrice.building_grade == building_grade,
                ConstructionUnitPrice.property_type == property_type,
            )
            .first()
        )
        return float(row.unit_price) if row else DEFAULT_CONSTRUCTION_UNIT_PRICE

    # ------------------------------------------------------------------
    # Khấu hao — tra bảng depreciation_rate trên DB
    # ------------------------------------------------------------------

    @staticmethod
    def _get_depreciation_rate(db: Session, building_grade: str) -> float:
        """Tra bảng khấu hao/năm theo building_grade."""
        row = (
            db.query(DepreciationRate.rate_per_year)
            .filter(DepreciationRate.building_grade == building_grade)
            .first()
        )
        return float(row.rate_per_year) if row else DEFAULT_DEPRECIATION_RATE

    # ------------------------------------------------------------------
    # Tuổi nhà
    # ------------------------------------------------------------------

    @staticmethod
    def _get_building_age(sample: dict) -> int:
        """Tuổi nhà = năm hiện tại - năm xây dựng."""
        building_info = sample.get("BuildingInfo", {})
        construction_year = building_info.get("ConstructionYear")
        if not construction_year:
            return 0
        age = datetime.date.today().year - construction_year
        return max(age, 0)

    # ------------------------------------------------------------------
    # Chi phí xây dựng còn lại
    # ------------------------------------------------------------------

    @classmethod
    def _estimate_construction_cost(cls, db: Session, sample: dict) -> Dict[str, Any]:
        """
        Chi phí xây dựng còn lại = đơn giá XD × diện tích XD × (1 - khấu hao lũy kế)
        Khấu hao lũy kế = tỷ lệ khấu hao/năm × tuổi nhà (tối đa 100%).
        """
        property_type = sample.get("property_type")

        building_info = sample.get("BuildingInfo", {})
        building_grade = building_info.get("building_grade")

        construction_area = (
            sample.get("TotalFloorArea")
            or building_info.get("Construction_Area")
            or building_info.get("ConstructionArea")
        )

        unit_price = cls._get_construction_unit_price(db, building_grade, property_type)
        raw_cost = unit_price * construction_area

        depreciation_rate_per_year = cls._get_depreciation_rate(db, building_grade)
        building_age = cls._get_building_age(sample)
        accumulated_depreciation = min(depreciation_rate_per_year * building_age, 1.0)

        construction_cost = raw_cost * (1 - accumulated_depreciation)

        return {
            "building_grade":             building_grade,
            "property_type":              property_type,
            "unit_price_xd":              unit_price,
            "TotalFloorArea":             construction_area,
            "building_age":               building_age,
            "depreciation_rate_per_year": depreciation_rate_per_year,
            "accumulated_depreciation":   accumulated_depreciation,
            "raw_construction_cost":      raw_cost,
            "construction_cost":          construction_cost,
        }

    # ------------------------------------------------------------------
    # Tổng giá trị = đất + xây dựng
    # ------------------------------------------------------------------

    @classmethod
    def _estimate_total_value(
        cls,
        db: Session,
        df: pd.DataFrame,
        sample: dict,
    ) -> Optional[Dict[str, Any]]:
        """
        Giá nhà = giá đất + chi phí xây dựng.
        Nếu PropertyType là "Đất" (đất thuần) -> chỉ tính giá đất.
        """
        land_result = cls._estimate_land_value(df, sample)
        if land_result is None:
            return None

        is_land_only = "đất" in str(sample.get("PropertyType", "")).lower()

        if is_land_only:
            land_result["construction_cost"] = 0
            land_result["total_value"] = land_result["land_value"]
            return land_result

        construction = cls._estimate_construction_cost(db, sample)
        land_result.update(construction)
        land_result["total_value"] = land_result["land_value"] + construction["construction_cost"]

        return land_result

    # ------------------------------------------------------------------
    # Pipeline chính — điểm truy cập cho API
    # ------------------------------------------------------------------

    @classmethod
    def calculate_ppcp(
        cls,
        sample: dict,
        db: Session,
    ) -> Optional[Dict[str, Any]]:
        """
        Pipeline chính:
        1. Chuẩn hoá tên phường / đường
        2. Query bảng giá đất nhà nước (bang_gia_dat) qua ORM
        3. Ước tính tổng giá trị (đất + xây dựng, khấu hao từ DB)

        Parameters
        ----------
        sample : dict
            Dữ liệu BĐS đầu vào (PropertyLocation, RoadAccessType, RoadWidth, land_area, …).
        db : Session
            SQLAlchemy ORM session.

        Returns
        -------
        dict hoặc None nếu không tra được bảng giá.
        """
        location = sample.get("PropertyLocation", {})
        ward   = normalize_text(location.get("Ward", ""))
        street = normalize_text(location.get("Street", ""))

        df = cls._query_land_price(db, ward, street)

        return cls._estimate_total_value(db, df, sample)
