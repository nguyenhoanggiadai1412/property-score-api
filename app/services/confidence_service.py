from datetime import datetime, date
from typing import List, Dict, Tuple, Optional, Any
from app.schemas.property import ValuationInputSchema

def score_so_luong(n: int) -> int:
    if n >= 5:
        return 100
    elif n >= 3:
        return 95
    elif n == 2:
        return 90
    elif n == 1:
        return 80
    else:
        return 45

def score_khoang_cach(avg_distance_m: float) -> int:
    if avg_distance_m <= 300:
        return 100
    elif avg_distance_m <= 500:
        return 95
    elif avg_distance_m <= 1000:
        return 90
    elif avg_distance_m <= 2000:
        return 80
    else:
        return 45

def score_thoi_gian(avg_days: float) -> int:
    if avg_days <= 30:
        return 100
    elif avg_days <= 90:
        return 95
    elif avg_days <= 180:
        return 85
    elif avg_days <= 365:
        return 70
    elif avg_days <= 730:
        return 50
    else:
        return 25

# Trọng số điểm nguồn dữ liệu
SOURCE_SCORE = {
    "cong_chung":   100,
    "registry":     100,
    "core_banking":  95,
    "third_party":   90,
    "khung_gia":     90,
    "listing":       85,
    "user_input":    80,
}

def score_nguon(source: str) -> int:
    return SOURCE_SCORE.get(source.lower(), 85)

def score_bien_gia(spread_pct: float) -> int:
    if spread_pct <= 5:
        return 100
    elif spread_pct <= 10:
        return 90
    elif spread_pct <= 15:
        return 80
    elif spread_pct <= 20:
        return 65
    elif spread_pct <= 30:
        return 45
    else:
        return 20

def calc_spread(p_list: list) -> float:
    if len(p_list) < 2:
        return 0.0
    pmax, pmin, pavg = max(p_list), min(p_list), sum(p_list) / len(p_list)
    return (pmax - pmin) / pavg * 100 if pavg else 0.0

# Trọng số cho tổng điểm tin cậy
WEIGHTS = {
    "so_luong":    0.15,
    "khoang_cach": 0.25,
    "thoi_gian":   0.25,
    "nguon":       0.20,
    "bien_gia":    0.15,
}

def overall_confidence(scores: dict) -> float:
    return sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)

def grade(cs: float) -> Tuple[str, str]:
    if cs >= 90:
        return "A", "Rất tin cậy"
    elif cs >= 80:
        return "B", "Tốt"
    elif cs >= 70:
        return "C", "Chấp nhận được"
    elif cs >= 50:
        return "D", "Rủi ro"
    else:
        return "E", "Không khuyến nghị"

def warnings(n_tsss: int, avg_distance_m: float, avg_days: float, spread_pct: float, source_score: float) -> List[str]:
    msgs = []
    if n_tsss < 3:
        msgs.append("Không đủ comparable (TSSS < 3)")
    if avg_distance_m > 2000:
        msgs.append("Comparables quá xa (Avg Distance > 2km)")
    if avg_days > 365:
        msgs.append("Giao dịch quá cũ (Avg Time > 1 năm)")
    if spread_pct > 20:
        msgs.append("Giá thị trường biến động mạnh (Spread > 20%)")
    if source_score < 50:
        msgs.append("Dữ liệu không đáng tin (Data Source score < 50)")
    return msgs

def days_since(transaction_date: str) -> float:
    if isinstance(transaction_date, str):
        transaction_date_obj = date.fromisoformat(transaction_date[:10])
    elif isinstance(transaction_date, datetime):
        transaction_date_obj = transaction_date.date()
    else:
        transaction_date_obj = transaction_date
    return (date.today() - transaction_date_obj).days

class ConfidenceService:
    @staticmethod
    def calculate_confidence_score(data: ValuationInputSchema) -> dict:
        """
        Tính điểm tin cậy tổng thể (Confidence Score) cho kết quả định giá AVM.
        """
        comps = data.ComparableAssets
        n = len(comps)

        # Lọc các TSSS có khoảng cách
        comps_with_dist = []
        for c in comps:
            if c.Comparable_Distances and len(c.Comparable_Distances) > 0:
                dist = c.Comparable_Distances[0].DistanceM
                if dist is not None:
                    comps_with_dist.append(c)

        # 1. Điểm số lượng TSSS
        k_so_luong = score_so_luong(n)

        # 2. Điểm khoảng cách trung bình
        if comps_with_dist:
            avg_dist = sum(c.Comparable_Distances[0].DistanceM for c in comps_with_dist) / len(comps_with_dist)
        else:
            avg_dist = 0.0
        k_khoang_cach = score_khoang_cach(avg_dist)

        # 3. Điểm thời gian giao dịch trung bình
        ages = []
        for c in comps:
            td = c.Comparable_Transaction.Transaction_Date
            if td:
                try:
                    ages.append(days_since(td))
                except Exception:
                    pass
        avg_days = sum(ages) / len(ages) if ages else 0.0
        k_thoi_gian = score_thoi_gian(avg_days)

        # 4. Điểm nguồn dữ liệu
        source_scores = []
        for c in comps:
            if c.data_source:
                source_scores.append(score_nguon(c.data_source))
        k_nguon = round(sum(source_scores) / len(source_scores)) if source_scores else 85

        # 5. Điểm biên giá (Spread)
        p_list = []
        for c in comps:
            price = c.Comparable_Transaction.Transaction_Price
            area = c.Comparable_Property_Detail.Land_Area
            if price and area:
                p_list.append(price / area)
        spread = calc_spread(p_list)
        k_bien_gia = score_bien_gia(spread)

        # 6. Tính điểm tin cậy tổng thể (Overall CS)
        scores = {
            "so_luong":    k_so_luong,
            "khoang_cach": k_khoang_cach,
            "thoi_gian":   k_thoi_gian,
            "nguon":       k_nguon,
            "bien_gia":    k_bien_gia,
        }
        cs = overall_confidence(scores)
        cs_grade, cs_meaning = grade(cs)

        # 7. Tạo danh sách các cảnh báo (Warnings)
        warns = warnings(n, avg_dist, avg_days, spread, k_nguon)

        return {
            "PropertyId":      data.PropertyId,
            "overall_score":   round(cs, 2),
            "grade":           cs_grade,
            "meaning":         cs_meaning,
            "component_scores": {
                "so_luong_tsss": {"score": float(k_so_luong),    "weight": "15%", "n": n},
                "khoang_cach":   {"score": float(k_khoang_cach), "weight": "25%", "avg_distance_m": round(avg_dist, 1)},
                "thoi_gian":     {"score": float(k_thoi_gian),   "weight": "25%", "avg_days": round(avg_days, 1)},
                "nguon_du_lieu": {"score": float(k_nguon),        "weight": "20%"},
                "bien_gia":      {"score": float(k_bien_gia),     "weight": "15%", "spread_pct": round(spread, 2)},
            },
            "warnings": warns,
        }
