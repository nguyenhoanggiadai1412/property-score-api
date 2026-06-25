from __future__ import annotations
from typing import Union, Optional
import statistics


# ---------------------------------------------------------------------------
# Bảng tra cứu
# ---------------------------------------------------------------------------

# 1.1. road_type – giá trị là string
ROAD_TYPE_TABLE: dict[str, float] = {
    "CBD":       1.00,
    "Trục chính": 0.85,
    "Khu vực":   0.70,
    "Nội khu":   0.55,
    "Đường nhỏ": 0.30,
}
ROAD_TYPE_W = 0.25

# 1.2. road_width – giá trị là số (mét), so sánh theo ngưỡng giảm dần
# Mỗi phần tử: (ngưỡng_tối_thiểu, K)
ROAD_WIDTH_BREAKS: list[tuple[float, float]] = [
    (20,  1.00),   # >20m
    (13,  0.95),   # 13–20m
    (9,   0.90),   # 9–13m
    (7,   0.85),   # 7–9m
    (5,   0.75),   # 5–7m
    (0,   0.40),   # <5m
]
ROAD_WIDTH_W = 0.20

# 1.3. poi_density – giá trị là số nguyên
POI_DENSITY_BREAKS: list[tuple[float, float]] = [
    (25, 1.00),   # ≥25
    (15, 0.80),   # 15–25
    (5,  0.60),   # 5–15
    (1,  0.40),   # 1–5
    (0,  0.20),   # 0
]
POI_DENSITY_W = 0.15

# 1.4. amenity – giá trị là số nhóm (0–4+)
AMENITY_BREAKS: list[tuple[float, float]] = [
    (4, 1.00),   # ≥4 nhóm
    (3, 0.80),   # 3 nhóm
    (2, 0.60),   # 2 nhóm
    (1, 0.40),   # 1 nhóm
    (0, 0.20),   # 0 nhóm
]
AMENITY_W = 0.10

# 1.5. sidewalk – giá trị là số (mét)
SIDEWALK_BREAKS: list[tuple[float, float]] = [
    (2, 1.00),   # >2m
    (0.001, 0.70),   # <2m (>0)
    (0, 0.40),   # 0 (không có)
]
SIDEWALK_W = 0.10

# 2.1. alley_cap  – giá trị là số nhóm (1–4)
ALLEY_CAP_BREAKS: list[tuple[float, float]] = [
    (1, .9),   # 1 nhóm
    (2, 0.75),   # 2 nhóm
    (3, 0.60),   # 3 nhóm
    (4, 0.45),   # 4 nhóm
]
ALLEY_CAP_W = 0.4

# 2.2. distance_main – giá trị là số (mét)
DISTANCE_MAIN_BREAKS: list[tuple[float, float]] = [
    (500, 0.50),   # >500m
    (200, 0.70),   # 200-500m 
    (50, 0.85),    # 50-200m 
    (0, 1),        # # >500m
]
DISTANCE_MAIN_W = 0.25

# 2.3. alley_level  – giá trị là số nhóm (1–4+)
ALLEY_LEVEL_BREAKS: list[tuple[float, float]] = [
    (4, .65),   # ≥4 nhóm
    (3, 0.8),   # 3 nhóm
    (2, 0.9),   # 2 nhóm
    (1, 1),   # 1 nhóm
]
ALLEY_LEVEL_W = 0.15

# 2.4. alley_type – giá trị là string
ALLEY_TYPE_TABLE: dict[str, float] = {
    "thông":    1.00,
    "cụt":      0.85,
}
ALLEY_TYPE_W = 0.1

# 2.5. alley_quality  – giá trị là string
ALLEY_QUALITY_TABLE: dict[str, float] = {
    "Tốt":          1.00,
    "Trung bình":   0.9,
    "Kém":          0.75,
    "Ngập":         0.6,
}
ALLEY_QUALITY_W = 0.1

# 3.1. Diện tích – giá trị là số (mét vuông)
LAND_AREA_BREAKS: list[tuple[float, float]] = [
    (120, 0.90),    # >120m²
    (80, 1),        # 80–120m²
    (60, 0.95),     # 60–<80m²
    (40, 0.90),     # 40–<60m²
    (0, 0.75),      # <40m²
]
LAND_AREA_W = 0.15

# 3.2. shape – giá trị là string
SHAPE_TABLE: dict[str, float] = {
    "Vuông":    1.00,
    "Méo":      0.9,
    "Gãy khúc": 0.75,
}
SHAPE_W = 0.1

# 3.3. ratio - 


# 3.4. 
REAR_SHAPE_TABLE: dict[str, float] = {
    "Nở hậu":    1.05,
    "Vuông":      1.00,
    "Thóp nhẹ":  0.90,
    "Thóp mạnh": 0.75,
}
REAR_SHAPE_W = 0.10

# 3.5. Mặt tiền
FRONTAGE_WIDTH_BREAKS: list[tuple[float, float]] = [
    (10, 1.10),   # >10m
    (6,  1.05),   # 6–10m
    (4,  1.00),   # 4–<6m
    (3,  0.85),   # 3–<4m
    (0,  0.70),   # <3m
]
FRONTAGE_WIDTH_W = 0.15
 
# 3.6. Mặt tiền
FRONTAGE_COUNT_BREAKS: list[tuple[float, float]] = [
    (2, 1.10),   # ≥2 MT
    (1, 1.00),   # 1 MT
]
FRONTAGE_COUNT_W = 0.10
 
# 3.7. Công trình
FLOOR_AREA_BREAKS: list[tuple[float, float]] = [
    (400, 1.10),   # >400m²
    (250, 1.05),   # 250–400m²
    (150, 1.00),   # 150–250m²
    (80,  0.90),   # 80–150m²
    (0,   0.80),   # <80m²
]
FLOOR_AREA_W = 0.10
 
# 3.8. Công trình
BUILDING_GRADE_TABLE: dict[str, float] = {
    "Cấp 1":   1.05,
    "Cấp 2":   1.00,
    "Cấp 3":   0.90,
    "Cấp 4":   0.80,
    "Nhà tạm": 0.60,
}
BUILDING_GRADE_W = 0.15
 
 # 4.1. school – d (m)
SCHOOL_BREAKS: list[tuple[float, float]] = [
    (0,   1.12),   # d ≤ 100m
    (100, 1.10),   # 100–300m
    (300, 1.00),   # 300–700m
    (700, 0.95),   # >700m
]
SCHOOL_W = 0.18

# 4.2. hospital – d (m); ≤50m được coi là quá gần → K thấp hơn
HOSPITAL_BREAKS: list[tuple[float, float]] = [
    (0,   0.98),   # d ≤ 50m
    (50,  1.05),   # 50–200m
    (200, 1.00),   # 200–500m
    (500, 0.95),   # >500m
]
HOSPITAL_W = 0.14

# 4.3. mall – d (m)
MALL_BREAKS: list[tuple[float, float]] = [
    (0,    1.12),   # ≤200m
    (200,  1.08),   # 200–500m
    (500,  1.00),   # 500–1000m
    (1000, 0.95),   # >1000m
]
MALL_W = 0.08

# 4.4. supermarket – d (m)
SUPERMARKET_BREAKS: list[tuple[float, float]] = [
    (0,   1.08),   # d ≤ 100m
    (100, 1.05),   # 100–300m
    (300, 1.00),   # 300–800m
    (800, 0.95),   # >800m
]
SUPERMARKET_W = 0.07

# 4.5. metro – d (m); <100m không có mức riêng → dùng mức 100–500m
METRO_BREAKS: list[tuple[float, float]] = [
    (0,    1.15),   # 100–500m  (gộp <100 vào đây vì không có mức riêng)
    (500,  1.10),   # 500–1000m
    (1000, 1.00),   # 1–2km
    (2000, 0.95),   # >2km
]
METRO_W = 0.13

# 4.6. park – d (m)
PARK_BREAKS: list[tuple[float, float]] = [
    (0,   1.10),   # d ≤ 100m
    (100, 1.08),   # 100–300m
    (300, 1.00),   # 300–800m
    (800, 0.95),   # >800m
]
PARK_W = 0.10

# 4.7. cbd distance – d (m)
CBD_DIST_BREAKS: list[tuple[float, float]] = [
    (0,    1.15),   # ≤1km
    (1000, 1.10),   # 1–3km
    (3000, 1.00),   # 3–5km
    (5000, 0.95),   # >5km
]
CBD_DIST_W = 0.10

# 4.8. admin_center – d (m); 200–500m là ngưỡng tốt nhất
ADMIN_CENTER_BREAKS: list[tuple[float, float]] = [
    (0,   1.05),   # ≤200m
    (200, 1.10),   # 200–500m
    (500, 1.00),   # 500–1500m
    (1500, 0.95),  # >1500m
]
ADMIN_CENTER_W = 0.04

# 4.9. market – d (m); ≤50m quá ồn → K thấp hơn
MARKET_BREAKS: list[tuple[float, float]] = [
    (0,   0.95),   # ≤50m
    (50,  1.05),   # 50–150m
    (150, 1.10),   # 150–300m
    (300, 1.00),   # 300–700m
    (700, 0.95),   # >700m
]
MARKET_W = 0.04

# 4.10. view – string: "river" | "sea" | None/other → K và W
VIEW_TABLE: dict[str, float] = {
    "Sông":   1.15,
    "Biển":   1.20,
    "Không":  1,
}
VIEW_W = 0.12

# 5.1. landfill – d (m)
LANDFILL_BREAKS: list[tuple[float, float]] = [
    (0,   0.50),   # d ≤ 50
    (50,  0.65),   # 50–100
    (100, 0.80),   # 100–200
    (200, 0.90),   # 200–500
    (500, 1.00),   # >500
]
LANDFILL_W = 0.22

# 5.2. wastewater – d (m)
WASTEWATER_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 50
    (50,  0.80),   # 50–150
    (150, 0.90),   # 150–300
    (300, 1.00),   # >300
]
WASTEWATER_W = 0.10

# 5.3. airport – d (m)
AIRPORT_BREAKS: list[tuple[float, float]] = [
    (0,    0.65),   # d ≤ 200
    (200,  0.75),   # 200–500
    (500,  0.85),   # 500–1000
    (1000, 0.92),   # 1000–2000
    (2000, 1.00),   # >2000
]
AIRPORT_W = 0.14

#  5.4. railway – d (m)
RAILWAY_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 30
    (30,  0.80),   # 30–100
    (100, 0.88),   # 100–300
    (300, 0.95),   # 300–700
    (700, 1.00),   # >700
]
RAILWAY_W = 0.10

#  5.5. emetery – d (m)
CEMETERY_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 50
    (50,  0.80),   # 50–150
    (150, 0.90),   # 150–300
    (300, 1.00),   # >300
]
CEMETERY_W = 0.12

#  5.6. funeral_home – d (m)
FUNERAL_HOME_BREAKS: list[tuple[float, float]] = [
    (0,   0.80),   # d ≤ 50
    (50,  0.85),   # 50–100
    (100, 0.92),   # 100–200
    (200, 1.00),   # >200
]
FUNERAL_HOME_W = 0.06

#  5.7. temple – d (m)
TEMPLE_BREAKS: list[tuple[float, float]] = [
    (0,   0.85),   # d ≤ 50
    (50,  0.90),   # 50–150
    (150, 0.95),   # 150–300
    (300, 1.00),   # >300
]
TEMPLE_W = 0.06

# ---------------------------------------------------------------------------
# Hàm tra cứu chung
# ---------------------------------------------------------------------------

def _lookup_by_threshold(value: float, breaks: list[tuple[float, float]]) -> float:
    """
    Trả về K tương ứng với ngưỡng đầu tiên mà value >= ngưỡng đó.
    breaks phải được sắp xếp giảm dần theo ngưỡng.
    """
    for threshold, k in breaks:
        if value >= threshold:
            return k
    # fallback: trả về K = 0
    return 0

def _score(value, weight: float, lookup_fn) -> float:
    if value is None:
        return 0.0
    return lookup_fn(value) * weight

# ---------------------------------------------------------------------------
# Hàm tính điểm từng feature
# ---------------------------------------------------------------------------

def score_road_type(value: str) -> float:
    if value is None:
        return 0
    k = ROAD_TYPE_TABLE.get(value)
    if k is None:
        return 0
    return k * ROAD_TYPE_W

def score_road_width(value) -> float:
    return _score(value, ROAD_WIDTH_W, lambda v: _lookup_by_threshold(float(v), ROAD_WIDTH_BREAKS))

def score_poi_density(value) -> float:
    return _score(value, POI_DENSITY_W, lambda v: _lookup_by_threshold(float(v), POI_DENSITY_BREAKS))

def score_amenity(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_cap(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_distance_main(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_level(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_type(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = ALLEY_TYPE_TABLE.get(value)
    if k is None:
        return 0
    return k * ALLEY_TYPE_W

def score_alley_quality(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = ALLEY_QUALITY_TABLE.get(value)
    if k is None:
        return 0
    return k * ALLEY_QUALITY_W

def score_sidewalk(value) -> float:
    return _score(value, SIDEWALK_W, lambda v: _lookup_by_threshold(float(v), SIDEWALK_BREAKS))

def score_area(value) -> float:
    return _score(value, LAND_AREA_W, lambda v: _lookup_by_threshold(float(v), LAND_AREA_BREAKS))

def score_shape(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = SHAPE_TABLE.get(value)
    if k is None:
        return 0
    return k * SHAPE_W

def score_rear_shape(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = REAR_SHAPE_TABLE.get(value)
    if k is None:
        return 0
    return k * REAR_SHAPE_W

def score_frontage_width(value) -> float:
    return _score(value, FRONTAGE_WIDTH_W, lambda v: _lookup_by_threshold(float(v), FRONTAGE_WIDTH_BREAKS))

def score_frontage_count(value) -> float:
    return _score(value, FRONTAGE_COUNT_W, lambda v: _lookup_by_threshold(float(v), FRONTAGE_COUNT_BREAKS))

def score_floor_area(value) -> float:
    return _score(value, FLOOR_AREA_W, lambda v: _lookup_by_threshold(float(v), FLOOR_AREA_BREAKS))

def score_building_grade(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = BUILDING_GRADE_TABLE.get(value)
    if k is None:
        return 0
    return k * BUILDING_GRADE_W

def score_school(value) -> float:
    return _score(value, SCHOOL_W, lambda v: _lookup_by_threshold(float(v), SCHOOL_BREAKS))

def score_hospital(value) -> float:
    return _score(value, HOSPITAL_W, lambda v: _lookup_by_threshold(float(v), HOSPITAL_BREAKS))

def score_mall(value) -> float:
    return _score(value, MALL_W, lambda v: _lookup_by_threshold(float(v), MALL_BREAKS))

def score_supermarket(value) -> float:
    return _score(value, SUPERMARKET_W, lambda v: _lookup_by_threshold(float(v), SUPERMARKET_BREAKS))

def score_metro(value) -> float:
    return _score(value, METRO_W, lambda v: _lookup_by_threshold(float(v), METRO_BREAKS))

def score_park(value) -> float:
    return _score(value, PARK_W, lambda v: _lookup_by_threshold(float(v), PARK_BREAKS))

def score_cbd_dist(value) -> float:
    return _score(value, CBD_DIST_W, lambda v: _lookup_by_threshold(float(v), CBD_DIST_BREAKS))

def score_admin_center(value) -> float:
    return _score(value, ADMIN_CENTER_W, lambda v: _lookup_by_threshold(float(v), ADMIN_CENTER_BREAKS))

def score_market(value) -> float:
    return _score(value, MARKET_W, lambda v: _lookup_by_threshold(float(v), MARKET_BREAKS))

def score_view(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = VIEW_TABLE.get(value)
    if k is None:
        return 0
    return k * VIEW_W

def score_landfill(value) -> float:
    return _score(value, LANDFILL_W, lambda v: _lookup_by_threshold(float(v), LANDFILL_BREAKS))

def score_wastewater(value) -> float:
    return _score(value, WASTEWATER_W, lambda v: _lookup_by_threshold(float(v), WASTEWATER_BREAKS))

def score_airport(value) -> float:
    return _score(value, AIRPORT_W, lambda v: _lookup_by_threshold(float(v), AIRPORT_BREAKS))

def score_railway(value) -> float:
    return _score(value, RAILWAY_W, lambda v: _lookup_by_threshold(float(v), RAILWAY_BREAKS))

def score_cemetery(value) -> float:
    return _score(value, CEMETERY_W, lambda v: _lookup_by_threshold(float(v), CEMETERY_BREAKS))

def score_funeral_home(value) -> float:
    return _score(value, FUNERAL_HOME_W, lambda v: _lookup_by_threshold(float(v), FUNERAL_HOME_BREAKS))

def score_temple(value) -> float:
    return _score(value, TEMPLE_W, lambda v: _lookup_by_threshold(float(v), TEMPLE_BREAKS))

# ===========================================================================
# WEIGHTS CỦA TỪNG FEATURE (để tính max_possible)
# ===========================================================================

FEATURE_WEIGHTS: dict[str, float] = {
    "road_type":       ROAD_TYPE_W,
    "road_width":      ROAD_WIDTH_W,
    "poi_density":     POI_DENSITY_W,
    "amenity":         AMENITY_W,
    "sidewalk":        SIDEWALK_W, # 5
    "alley_cap":       ALLEY_CAP_W,
    "distance_main":   DISTANCE_MAIN_W,
    "alley_level":     ALLEY_LEVEL_W,
    "alley_type":      ALLEY_TYPE_W,
    "alley_quality":   ALLEY_QUALITY_W, # 5
    "area":            LAND_AREA_W,
    "shape":           SHAPE_W,
    #"ratio":           RATIO_W,
    "rear_shape":      REAR_SHAPE_W,
    "frontage_width":  FRONTAGE_WIDTH_W,
    "frontage_count":  FRONTAGE_COUNT_W,
    "floor_area":      FLOOR_AREA_W,
    "building_grade":  BUILDING_GRADE_W, # 8
    "Nearest_School":  SCHOOL_W,
    "Nearest_Hospital":HOSPITAL_W,
    "Nearest_mall":    MALL_W,
    "supermarket":     SUPERMARKET_W,
    "metro":           METRO_W,
    "park":            PARK_W,
    "cbd_dist":        CBD_DIST_W,
    "admin_center":    ADMIN_CENTER_W,
    "Nearest_Market":  MARKET_W,
    "view":            VIEW_W, # 10
    "Nearest_landfill":LANDFILL_W,
    "wastewater":      WASTEWATER_W,
    "Nearest_Airport": AIRPORT_W,
    "Nearest_Railway": RAILWAY_W,
    "Nearest_cemetery":CEMETERY_W,
    "funeral_home":    FUNERAL_HOME_W,
    "Nearest_Pagoda":  TEMPLE_W, # 7
}

SCORE_FUNCTIONS = {
    "road_type":       score_road_type,
    "road_width":      score_road_width,
    "poi_density":     score_poi_density,
    "amenity":         score_amenity,
    "sidewalk":        score_sidewalk,
    "alley_cap":       score_alley_cap,
    "distance_main":   score_distance_main,
    "alley_level":     score_alley_level,
    "alley_type":      score_alley_type,
    "alley_quality":   score_alley_quality, # 5
    "area":            score_area,
    "shape":           score_shape,
    #"ratio":           score_ratio,
    "rear_shape":      score_rear_shape,
    "frontage_width":  score_frontage_width,
    "frontage_count":  score_frontage_count,
    "floor_area":      score_floor_area,
    "building_grade":  score_building_grade,
    "Nearest_School":  score_school,
    "Nearest_Hospital":score_hospital,
    "Nearest_mall":    score_mall,
    "supermarket":     score_supermarket,
    "metro":           score_metro,
    "park":            score_park,
    "cbd_dist":        score_cbd_dist,
    "admin_center":    score_admin_center,
    "Nearest_Market":  score_market,
    "view":            score_view,
    "Nearest_landfill":score_landfill,
    "wastewater":      score_wastewater,
    "Nearest_Airport": score_airport,
    "Nearest_Railway": score_railway,
    "Nearest_cemetery":score_cemetery,
    "funeral_home":    score_funeral_home,
    "Nearest_Pagoda":  score_temple,
}

# ---------------------------------------------------------------------------
# Hàm tổng hợp
# ---------------------------------------------------------------------------

def calculate_f_score(house: dict) -> dict:
    breakdown: dict[str, float] = {}
    max_possible = 0.0

    for feature, fn in SCORE_FUNCTIONS.items():
        value = house.get(feature)   # None nếu thiếu
        weighted = fn(value)
        breakdown[feature] = round(weighted, 4)
        #max_possible += FEATURE_WEIGHTS[feature]   # luôn cộng W, kể cả khi value=None (K=0)

    total = sum(breakdown.values())
    return total
    # return {
    #     "total_score": round(total, 4),
    #     #"normalized":  round(total / max_possible, 4),
    #     "breakdown":   {k: round(v, 4) for k, v in breakdown.items()},
    # }

def calculate_P_by_f_score(data: dict) -> dict:
    target = flatten_external_target(data)
    f_target = calculate_f_score(target)
    results = []

    for i, comp_raw in enumerate(data.get("Comparable_Assets", [])):
        comp = flatten_external_comp(comp_raw)
        f_comp = calculate_f_score(comp)

        price = comp_raw.get("Comparable_Transaction", {}).get("Transaction_Price")
        area  = comp_raw.get("Comparable_Property_Detail", {}).get("Land_Area")
        target_area = data.get("land_area")

        p = (
            price * f_target * target_area / (f_comp * area)
            if (f_comp != 0 and price and area and target_area) else None
        )
        results.append({
            "Comparable_id": comp.get("Comparable_id"),
            "price": price,
            "f_score": round(f_comp, 4),
            "P_tsmt": round(p) if p else None,
            #"k*W": f_target['breakdown']
        })

    return {
        "target_asset": {
            "PropertyId": target.get("PropertyId"),
            "f_score": round(f_target, 4),
            #"k*W": f_comp['breakdown']
        },

        "Comparable_Assets": results
    }


# ---------------------------------------------------------------------------
# flatten json -> dict (theo schema bên ngoài)
# ---------------------------------------------------------------------------
def flatten(asset: dict) -> dict:
    """
    Flatten asset:
    - giữ các field thường
    - bung các dict con (nearby, features, ...)
    - bỏ dict lồng sâu hơn
    """
    result = {}

    for k, v in asset.items():
        # dict con -> bung ra
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                # chỉ lấy primitive
                if not isinstance(sub_v, dict):
                    result[sub_k] = sub_v
        else:
            result[k] = v

    return result

def flatten_external_target(data: dict) -> dict:
    """
    Flatten target asset từ schema bên ngoài sang dict phẳng cho calculate_f_score.
    """
    loc  = data.get("PropertyLocation", {})
    adv  = data.get("Advantages", {})

    return {
        # Đường / hẻm
        "road_width":      data.get("RoadWidth"),
        "frontage_width":  data.get("FrontageWidth"),
        "frontage_count":  data.get("frontage_count"),
        "distance_main":   data.get("distance_to_main_road"),
        # Đất
        "area":            data.get("land_area"),
        "floor_area":      data.get("Construction_Area"),
    }

def flatten_external_target(data: dict) -> dict:
    target_raw = flatten(data)
 
    # Override các key bị đặt tên khác so với SCORE_FUNCTIONS
    info = data.get("BuildingInfo", {})
    target_raw["road_type"]      = data.get("RoadAccessType")
    target_raw["road_width"]     = data.get("RoadWidth")
    target_raw["distance_main"]  = data.get("distance_to_main_road")
    target_raw["area"]           = data.get("land_area")
    target_raw["floor_area"]     = data.get("Construction_Area") or info.get("ConstructionArea")# or info.get("TotalFloorArea")
  
    return target_raw

def flatten_external_comp(comp: dict) -> dict:
    comp_raw = flatten(comp)
 
    # Override các key bị đặt tên khác trong Comparable_Property_Detail
    d = comp.get("Comparable_Property_Detail", {})
    comp_raw["area"]           = d.get("Land_Area")
    comp_raw["frontage_width"] = d.get("Frontage")
    comp_raw["road_width"]     = d.get("Road_width")
    comp_raw["floor_area"]     = d.get("Building_Area")

    return comp_raw

# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

def calculate_benchmark(data: dict) -> dict:
    """
    Đầu vào: Json mau
    Tính benchmark từ P_tsmt của từng comparable (đơn giá = Transaction_Price / Land_Area).
    Trả về data gốc được bổ sung key "benchmark".
    """
    comps = data.get("Comparable_Assets", [])

    p_list = []
    for c in comps:
        p_tsmt = c.get("Comparable_Transaction", {}).get("Transaction_Price")
        area   = c.get("Comparable_Property_Detail", {}).get("Land_Area")
        if p_tsmt and area:
            p_list.append(p_tsmt / area)

    p_min = min(p_list)
    p_max = max(p_list)

    data["benchmark"] = {
        "average":   round(sum(p_list) / len(p_list)),
        "median":    round(statistics.median(p_list)),
        "min":       p_min,
        "max":       p_max,
        "range":     p_max - p_min,
        "n_samples": len(p_list),
    }
    return data

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    sample = {
  "PropertyId": "TSMT631850",
  "PropertyType": "Nha_o",
 # "CollateralFlag": false,
  "OwnershipPercentage": 0,
  "DisputeFlag": "Khong_tranh_chap",
  #"MortgageFlag": false,
  "LandUsePurpose": "ODT___t______th_",
  "RoadAccessType": "M_t_ti_n",
  "RoadWidth": 10,
 # "AlleyFlag": false,
  "Version": 0,
  "frontage_count": 1,
  "distance_to_main_road": 10,
  "Construction_Area": 80,
 # "Property_On_land": false,
  "structure_type": "B__t_ng_c_t_th_p",
  "BuildingInfo": {
 #   "BuildingFlag": false,
    "TotalFloorArea": 0,
    "ConstructionArea": 0,
    "NumberOfFloors": 2,
    "ConstructionYear": 2004
  },
  "PropertyLocation": {
    "HouseNumber": "88",
    "Street": "Lê Lợi",
    "Ward": "Phường Bến Thành",
    "Province": "Thành phố Hồ Chí Minh",
    "Latitude": 10.77293005,
    "Longitude": 106.6993318,
    "LocationScore": 0
  },
  "Owner_": {},
  "Comparable_Assets": [
    {
      "Comparable_id": "117.47196215",
      "property_type": "Nhà mặt phố",
      "address": "Đường Lý Tự Trọng, Phường Bến Thành, Quận 1, Hồ Chí Minh",
      "ward": "Phường Bến Thành",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.77413995,
      "longtitude": 106.6978222,
      "Note": "Vị trí vàng - MT Lý Tự Trọng, Quận 1 - 8x20m - 4 Tầng - HĐT 250 triệu/tháng - giá 100 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 1600,
        "Building_Area": 0,
        "Frontage": 80,
        "Road_width": 0,
        "Floor_Count": 40,
        "Construction_year": 0,
        "Legal_status": "khác"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 1000000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-09T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {},
      "Comparable_Distances": [
        {
          "DistanceM": 212.53325933
        }
      ]
    },
    {
      "Comparable_id": "117.4599718",
      "property_type": "Nhà mặt phố",
      "address": "Đường Bùi Viện, Phường Phạm Ngũ Lão, Quận 1, Hồ Chí Minh",
      "ward": "Phường Phạm Ngũ Lão",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.7670049,
      "longtitude": 106.6929669,
      "Note": "Khu vip bán nhà 2 tầng mặt tiền 8m xe hơi đ.Bùi Viện, Q.1- dt 3,2m*11m sh vuông đẹp- chủ 1 đời xưa",
      "Comparable_Property_Detail": {
        "Land_Area": 360,
        "Building_Area": 0,
        "Frontage": 35,
        "Road_width": 0,
        "Floor_Count": 20,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 184000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-07T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 315.2,
        "Nearest_Hospital": 212.7,
        "Nearest_Market": 72,
        "Nearest_Airport": 6996.3,
        "Nearest_Railway": 694.1,
        "Nearest_landfill": 6399.9,
        "Nearest_mall": 570.8,
        "Nearest_Pagoda": 146.8
      },
      "Comparable_Distances": [
        {
          "DistanceM": 956.11512178
        }
      ]
    },
    {
      "Comparable_id": "117.46514059",
      "property_type": "Nhà mặt phố",
      "address": "Đường Ký Con, Phường Bến Thành, Quận 1, Hồ Chí Minh",
      "ward": "Phường Bến Thành",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.76717389,
      "longtitude": 106.6979667,
      "Note": "Ngộp bank bán gấp 3 mặt tiền P. Bến Thành - Q.1. HĐT: 85tr. DT: 6x19m. 115m2. 3 tầng. Giá 30 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 1150,
        "Building_Area": 0,
        "Frontage": 60,
        "Road_width": 0,
        "Floor_Count": 30,
        "Construction_year": 0,
        "Legal_status": "khác"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 300000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-07T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 181,
        "Nearest_Hospital": 146.2,
        "Nearest_Market": 69.1,
        "Nearest_Airport": 7313.3,
        "Nearest_Railway": 420.3,
        "Nearest_landfill": 6140.6,
        "Nearest_mall": 73.5,
        "Nearest_Pagoda": 92.8
      },
      "Comparable_Distances": [
        {
          "DistanceM": 772.09084804
        },
        {
          "DistanceM": 653.97743068
        }
      ]
    },
    {
      "Comparable_id": "117.4720141",
      "property_type": "Nhà riêng",
      "address": "Đường Lê Thánh Tôn, Phường Bến Thành, Quận 1, Hồ Chí Minh",
      "ward": "Phường Bến Thành",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.773729,
      "longtitude": 106.6982851,
      "Note": "Nhà trung tâm quận 1 cách mặt tiền Lê Thánh Tôn chỉ 50m - Giá tốt hiếm có 4x20m 3 lầu giá 25.5 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 800,
        "Building_Area": 0,
        "Frontage": 0,
        "Road_width": 0,
        "Floor_Count": 40,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 250000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-10T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 364,
        "Nearest_Hospital": 109.8,
        "Nearest_Market": 132.2,
        "Nearest_Airport": 6786.9,
        "Nearest_Railway": 312.6,
        "Nearest_landfill": 5466.7,
        "Nearest_mall": 258.3,
        "Nearest_Pagoda": 191.9
      },
      "Comparable_Distances": [
        {
          "DistanceM": 227.19426832
        },
        {
          "DistanceM": 144.62083686
        }
      ]
    },
    {
      "Comparable_id": "117.4655202",
      "property_type": "Nhà mặt phố",
      "address": "Đường Ký Con, Phường Nguyễn Thái Bình, Quận 1, Hồ Chí Minh",
      "ward": "Phường Nguyễn Thái Bình",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.767189,
      "longtitude": 106.6983312,
      "Note": "Bán nhà Ký Con 68.8m² - mặt tiền - 4 tầng - Quận 1 - giá 36 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 690,
        "Building_Area": 0,
        "Frontage": 0,
        "Road_width": 0,
        "Floor_Count": 0,
        "Construction_year": 0,
        "Legal_status": "khác"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 360000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-10T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {},
      "Comparable_Distances": [
        {
          "DistanceM": 757.89019458
        },
        {
          "DistanceM": 644.39587683
        }
      ]
    },
    {
      "Comparable_id": "117.46679302",
      "property_type": "Nhà mặt phố",
      "address": "Đường Calmette, Phường Nguyễn Thái Bình, Quận 1, Hồ Chí Minh",
      "ward": "Phường Nguyễn Thái Bình",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.76670092,
      "longtitude": 106.7000921,
      "Note": "Bán nhà Calmette 310m² - mặt tiền - ngang 13m - 4 tầng - Quận 1 - giá 385 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 3100,
        "Building_Area": 0,
        "Frontage": 0,
        "Road_width": 0,
        "Floor_Count": 0,
        "Construction_year": 0,
        "Legal_status": "khác"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 3850000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-10T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 217.9,
        "Nearest_Hospital": 280.5,
        "Nearest_Market": 229.9,
        "Nearest_Airport": 7502.3,
        "Nearest_Railway": 531,
        "Nearest_landfill": 6098.2,
        "Nearest_mall": 211.5,
        "Nearest_Pagoda": 187.3
      },
      "Comparable_Distances": [
        {
          "DistanceM": 779.1496734
        },
        {
          "DistanceM": 694.02279046
        }
      ]
    },
    {
      "Comparable_id": "117.47332999",
      "property_type": "Nhà mặt phố",
      "address": "Đường Hàm Nghi, Phường Nguyễn Thái Bình, Quận 1, Hồ Chí Minh",
      "ward": "Phường Nguyễn Thái Bình",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.77064839,
      "longtitude": 106.7026816,
      "Note": "Bán nhà mặt tiền 5 tầng Hàm Nghi , P. Nguyễn Thái Bình Quận 1 DT: 4x17m giá 66.5 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 665,
        "Building_Area": 0,
        "Frontage": 500,
        "Road_width": 0,
        "Floor_Count": 50,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 665000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-04-30T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 100.2,
        "Nearest_Hospital": 380.5,
        "Nearest_Market": 148.2,
        "Nearest_Airport": 7367,
        "Nearest_Railway": 522.5,
        "Nearest_landfill": 5585.7,
        "Nearest_mall": 305.4,
        "Nearest_Pagoda": 168.4
      },
      "Comparable_Distances": [
        {
          "DistanceM": 425.75691882
        },
        {
          "DistanceM": 444.88592949
        }
      ]
    },
    {
      "Comparable_id": "117.47725432",
      "property_type": "Nhà mặt phố",
      "address": "Đường Lê Thánh Tôn, Phường Bến Nghé, Quận 1, Hồ Chí Minh",
      "ward": "Phường Bến Nghé",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.77628352,
      "longtitude": 106.7009708,
      "Note": "Chính chủ bán nhà MT Lê Thánh Tôn, P.Bến Nghé, Quận 1 ( 5.5x27.5m ) 7 Tầng mới. Giá 104 tỷ tl",
      "Comparable_Property_Detail": {
        "Land_Area": 1400,
        "Building_Area": 0,
        "Frontage": 55,
        "Road_width": 0,
        "Floor_Count": 0,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 1040000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-04T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 340.4,
        "Nearest_Hospital": 407.5,
        "Nearest_Market": 465.7,
        "Nearest_Airport": 6793.4,
        "Nearest_Railway": 162.2,
        "Nearest_landfill": 5082,
        "Nearest_mall": 299.7,
        "Nearest_Pagoda": 252.7
      },
      "Comparable_Distances": [
        {
          "DistanceM": 289.13371736
        },
        {
          "DistanceM": 411.98039233
        }
      ]
    },
    {
      "Comparable_id": "117.46017275",
      "property_type": "Nhà mặt phố",
      "address": "Đường Cô Bắc, Phường Cầu Ông Lãnh, Quận 1, Hồ Chí Minh",
      "ward": "Phường Cầu Ông Lãnh",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.76505805,
      "longtitude": 106.6951147,
      "Note": "Nhà mặt tiền ngang 4.3x16m đường Cô Bắc, Quận 1 giá chỉ 23 tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 660,
        "Building_Area": 0,
        "Frontage": 43,
        "Road_width": 0,
        "Floor_Count": 30,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 230000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-04-27T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 159.7,
        "Nearest_Hospital": 206.5,
        "Nearest_Market": 255.4,
        "Nearest_Airport": 7309.5,
        "Nearest_Railway": 722.3,
        "Nearest_landfill": 6485.7,
        "Nearest_mall": 369.4,
        "Nearest_Pagoda": 87.3
      },
      "Comparable_Distances": [
        {
          "DistanceM": 985.35941624
        }
      ]
    },
    {
      "Comparable_id": "117.46176141",
      "property_type": "Nhà riêng",
      "address": "Đường Lê Thị Riêng, Phường Bến Thành, Quận 1, Hồ Chí Minh",
      "ward": "Phường Bến Thành",
      "district": "Quận 1",
      "province": "Hồ Chí Minh",
      "Latitude": 10.77107471,
      "longtitude": 106.6906867,
      "Note": "Bán nhà ngay ngã 6 Phù Đổng Quận 1, ngang ~5m, 4 tầng 5 ngủ nhà mới đẹp ô tô đậu ở nhà 23tỷ",
      "Comparable_Property_Detail": {
        "Land_Area": 620,
        "Building_Area": 0,
        "Frontage": 49,
        "Road_width": 0,
        "Floor_Count": 40,
        "Construction_year": 0,
        "Legal_status": "sổ đỏ/sổ hồng"
      },
      "Comparable_Transaction": {
        "Transaction_Price": 230000000000,
        "Listing_Price": 0,
        "Price_Per_m2": 0,
        "Transaction_Date": "2026-05-10T17:00:00.000Z",
        "Distance_To_Subject": 0
      },
      "Advantages": {
        "Nearest_School": 40.1,
        "Nearest_Hospital": 43,
        "Nearest_Market": 448.6,
        "Nearest_Airport": 6483,
        "Nearest_Railway": 787.1,
        "Nearest_landfill": 6136.3,
        "Nearest_mall": 777.3,
        "Nearest_Pagoda": 311.3
      },
      "Comparable_Distances": [
        {
          "DistanceM": 967.53619014
        }
      ]
    }
  ],
  "Legal_Certificate": {},
  "Advantages": {
    "Nearest_School": 283.6,
    "Nearest_Hospital": 103.2,
    "Nearest_Market": 149.2,
    "Nearest_Airport": 6930.1,
    "Nearest_Railway": 271.6,
    "Nearest_landfill": 5496.1,
    "Nearest_mall": 137.9,
    "Nearest_Pagoda": 161.4
  },
  "land_area": 100,
  "frontage_width": 10,
  "LocationType": "Moi",
  "LandAreaTotal": 0,
  "FrontageWidth": 0
}

    #target = flatten_external_target(sample)
    result = calculate_P_by_f_score(sample)
    #print("Input:", json.dumps(sample, ensure_ascii=False, indent=2))
    print("\nOutput:")
    #print(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

