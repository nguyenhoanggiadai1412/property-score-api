from __future__ import annotations
from sqlalchemy import create_engine, text
import pandas as pd
import statistics


# ---------------------------------------------------------------------------
# FeatureRules — load toàn bộ weight + lookup từ PG, không hardcode rule nào.
#
# Schema PG:
#   lookup_feature(feature_code PK, feature_name, weight)
#   lookup_value(id PK, feature_code, min_value, max_value, text_value, score)
#
# Muốn sửa rule (breaks/threshold/category/weight) -> sửa trực tiếp trên PG,
# không cần đổi code hay deploy lại API.
# ---------------------------------------------------------------------------

class FeatureRules:
    def __init__(self, engine):
        self.weights: dict[str, float] = {}
        self.numeric_rules: dict[str, list[tuple]] = {}     # feature_code -> [(min,max,score)]
        self.category_rules: dict[str, dict[str, float]] = {}  # feature_code -> {text_lower: score}
        self._load(engine)

    def _load(self, engine):
        with engine.connect() as conn:
            weight_df = pd.read_sql(text("SELECT feature_code, weight FROM lookup_feature"), conn)
            value_df  = pd.read_sql(text("SELECT feature_code, min_value, max_value, text_value, score FROM lookup_value"), conn)

        self.weights = dict(zip(weight_df["feature_code"], weight_df["weight"]))

        for feature_code, group in value_df.groupby("feature_code"):
            is_numeric = group["text_value"].isna().all()
            if is_numeric:
                rows = [
                    (
                        None if pd.isna(r.min_value) else r.min_value,
                        None if pd.isna(r.max_value) else r.max_value,
                        r.score,
                    )
                    for r in group.itertuples()
                ]
                rows.sort(key=lambda r: (r[0] if r[0] is not None else float("-inf")), reverse=True)
                self.numeric_rules[feature_code] = rows
            else:
                self.category_rules[feature_code] = {
                    str(r.text_value).strip().lower(): r.score
                    for r in group.itertuples() if r.text_value is not None
                }

    def score_feature(self, feature_code: str, value) -> dict:
        """
        Trả về chi tiết K, W, K*W cho 1 feature.
        K = 0 nếu thiếu dữ liệu hoặc không khớp rule nào.
        """
        w = self.weights.get(feature_code, 0.0)

        if value is None:
            return {"value": None, "k": 0.0, "w": w, "weighted": 0.0}

        if feature_code in self.numeric_rules:
            try:
                v = float(value)
            except (TypeError, ValueError):
                return {"value": value, "k": 0.0, "w": w, "weighted": 0.0}
            for min_v, max_v, score in self.numeric_rules[feature_code]:
                lower_ok = (min_v is None) or (v >= min_v)
                upper_ok = (max_v is None) or (v < max_v)
                if lower_ok and upper_ok:
                    k = float(score)
                    return {"value": value, "k": k, "w": w, "weighted": k * w}
            return {"value": value, "k": 0.0, "w": w, "weighted": 0.0}

        if feature_code in self.category_rules:
            k = self.category_rules[feature_code].get(str(value).strip().lower())
            if k is not None:
                return {"value": value, "k": float(k), "w": w, "weighted": float(k) * w}
            return {"value": value, "k": 0.0, "w": w, "weighted": 0.0}

        return {"value": value, "k": 0.0, "w": w, "weighted": 0.0}

    def all_feature_codes(self) -> list[str]:
        return list(self.weights.keys())


# ---------------------------------------------------------------------------
# Hàm tổng hợp f-score
# ---------------------------------------------------------------------------

def calculate_f_score(house: dict, rules: FeatureRules) -> dict:
    """
    house: dict đã flatten, key = feature_code khớp với PG (Nearest_School, road_width, ...).
    Trả về:
        {
            "total_score": float,
            "breakdown": { feature_code: {"value":..., "k":..., "w":..., "weighted":...}, ... }
        }
    """
    breakdown = {}
    total = 0.0
    for feature_code in rules.all_feature_codes():
        detail = rules.score_feature(feature_code, house.get(feature_code))
        breakdown[feature_code] = {
            "value":    detail["value"],
            "k":        round(detail["k"], 4),
            "w":        detail["w"],
            "weighted": round(detail["weighted"], 4),
        }
        total += detail["weighted"]

    return {
        "total_score": round(total, 4),
        #"breakdown":   breakdown,
    }


def calculate_P_by_f_score(data: dict, rules: FeatureRules) -> dict:
    target = flatten_external_target(data)
    f_target_result = calculate_f_score(target, rules)
    f_target = f_target_result["total_score"]
    results = []

    for comp_raw in data.get("Comparable_Assets", []):
        comp = flatten_external_comp(comp_raw)
        f_comp_result = calculate_f_score(comp, rules)
        f_comp = f_comp_result["total_score"]

        price = comp_raw.get("Comparable_Transaction", {}).get("Transaction_Price")
        area  = comp_raw.get("Comparable_Property_Detail", {}).get("Land_Area")
        target_area = data.get("land_area")

        p = (
            price * f_target * target_area / (f_comp * area)
            if (f_comp != 0 and price and area and target_area) else None
        )
        results.append({
            "Comparable_id": comp_raw.get("Comparable_id"),
            "price": price,
            "f_score": f_comp,
            "P_tsmt": round(p) if p else None,
            #"breakdown": f_comp_result["breakdown"],
        })

    return {
        "target_asset": {
            "PropertyId": data.get("PropertyId"),
            "f_score": f_target,
            #"breakdown": f_target_result["breakdown"],
        },
        "Comparable_Assets": results,
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
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if not isinstance(sub_v, dict):
                    result[sub_k] = sub_v
        else:
            result[k] = v
    return result


def flatten_external_target(data: dict) -> dict:
    target_raw = flatten(data)

    # Override các key bị đặt tên khác so với feature_code trên PG
    info = data.get("BuildingInfo", {})
    target_raw["road_type"]     = data.get("RoadAccessType")
    target_raw["road_width"]    = data.get("RoadWidth")
    target_raw["distance_main"] = data.get("distance_to_main_road")
    target_raw["area"]          = data.get("land_area")
    target_raw["floor_area"]    = data.get("Construction_Area") or info.get("ConstructionArea")

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
    Tính benchmark từ đơn giá = Transaction_Price / Land_Area của từng comparable.
    Trả về data gốc được bổ sung key "benchmark".
    """
    comps = data.get("Comparable_Assets", [])

    p_list = []
    for c in comps:
        price = c.get("Comparable_Transaction", {}).get("Transaction_Price")
        area  = c.get("Comparable_Property_Detail", {}).get("Land_Area")
        if price and area:
            p_list.append(price / area)

    if not p_list:
        data["benchmark"] = None
        return data

    p_min, p_max = min(p_list), max(p_list)
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

# if __name__ == "__main__":
#     import json

#     engine = create_engine("postgresql+psycopg2://postgres:123456@192.168.1.22:5433/gisdb")
#     rules = FeatureRules(engine)   # load 1 lần, dùng lại cho mọi request

#     sample = {
#         "PropertyId": "TSMT631850",
#         "PropertyType": "Nha_o",
#         "RoadAccessType": "Mặt tiền",
#         "RoadWidth": 10,
#         "frontage_count": 1,
#         "distance_to_main_road": 10,
#         "Construction_Area": 80,
#         "BuildingInfo": {
#             "TotalFloorArea": 0,
#             "ConstructionArea": 0,
#             "NumberOfFloors": 2,
#             "ConstructionYear": 2004,
#         },
#         "Advantages": {
#             "Nearest_School": 283.6,
#             "Nearest_Hospital": 103.2,
#             "Nearest_Market": 149.2,
#             "Nearest_Airport": 6930.1,
#             "Nearest_Railway": 271.6,
#             "Nearest_landfill": 5496.1,
#             "Nearest_mall": 137.9,
#             "Nearest_Pagoda": 161.4,
#         },
#         "land_area": 100,
#         "frontage_width": 10,
#         "Comparable_Assets": [
#             {
#                 "Comparable_id": "117.46679302",
#                 "Comparable_Property_Detail": {
#                     "Land_Area": 3100, "Frontage": 0, "Road_width": 0, "Building_Area": 0,
#                 },
#                 "Comparable_Transaction": {"Transaction_Price": 3850000000000},
#                 "Advantages": {
#                     "Nearest_School": 217.9, "Nearest_Hospital": 280.5, "Nearest_Market": 229.9,
#                     "Nearest_Airport": 7502.3, "Nearest_Railway": 531, "Nearest_landfill": 6098.2,
#                     "Nearest_mall": 211.5, "Nearest_Pagoda": 187.3,
#                 },
#             },
#         ],
#     }

#     result = calculate_P_by_f_score(sample, rules)
#     print(json.dumps(calculate_benchmark(sample), ensure_ascii=False, indent=2))
#     #print(json.dumps(flatten_external_target(sample), ensure_ascii=False, indent=2))