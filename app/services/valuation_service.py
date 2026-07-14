import statistics
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.schemas.property import ValuationInputSchema, ComparableAssetSchema
from app.services.rules_service import RulesService

def flatten_dict(d: dict) -> dict:
    """
    Làm phẳng dictionary:
    - Giữ các trường dữ liệu nguyên bản (primitive values).
    - Bung các dictionary con 1 cấp ra ngoài.
    """
    flat = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if not isinstance(sub_v, dict) and not isinstance(sub_v, list):
                    flat[sub_k] = sub_v
        else:
            if not isinstance(v, dict) and not isinstance(v, list):
                flat[k] = v
    return flat

def flatten_target_asset(data: ValuationInputSchema) -> dict:
    """
    Làm phẳng tài sản mục tiêu (Target Asset) và ánh xạ các trường khác biệt.
    """
    raw_dict = data.model_dump()
    flat = flatten_dict(raw_dict)
    
    # Ánh xạ các key khác biệt so với feature_code trên DB
    info = raw_dict.get("BuildingInfo") or {}
    flat["road_type"]     = raw_dict.get("RoadAccessType")
    flat["road_width"]    = raw_dict.get("RoadWidth")
    flat["distance_main"] = raw_dict.get("distance_to_main_road")
    flat["area"]          = raw_dict.get("land_area")
    
    # Chọn floor_area ưu tiên từ root rồi đến BuildingInfo
    flat["floor_area"]    = raw_dict.get("Construction_Area") or info.get("ConstructionArea") or info.get("TotalFloorArea")
    
    # Đưa các Advantages vào dictionary phẳng để so khớp rule
    adv = raw_dict.get("Advantages") or {}
    for k, v in adv.items():
        if v is not None:
            flat[k] = v
            
    return flat

def flatten_comparable_asset(comp: ComparableAssetSchema) -> dict:
    """
    Làm phẳng tài sản so sánh (Comparable Asset) và ánh xạ các trường khác biệt.
    """
    raw_dict = comp.model_dump()
    flat = flatten_dict(raw_dict)
    
    # Ánh xạ các key khác biệt trong Comparable_Property_Detail
    d = raw_dict.get("Comparable_Property_Detail") or {}
    flat["area"]           = d.get("Land_Area")
    flat["frontage_width"] = d.get("Frontage")
    flat["road_width"]     = d.get("Road_width")
    flat["floor_area"]     = d.get("Building_Area")
    
    # Đưa các Advantages của TSSS vào dictionary phẳng
    adv = raw_dict.get("Advantages") or {}
    for k, v in adv.items():
        if v is not None:
            flat[k] = v
            
    return flat

class ValuationService:
    @staticmethod
    def calculate_f_score(flat_asset: dict, rules: RulesService) -> float:
        """
        Tính điểm F-Score tổng hợp dựa trên các rules.
        """
        total = 0.0
        for feature_code in rules.get_all_features():
            weighted = rules.calculate_weighted_score(feature_code, flat_asset.get(feature_code))
            total += weighted
        return round(total, 4)

    @classmethod
    def calculate_compare_price(cls, data: ValuationInputSchema, db: Session) -> dict:
        """
        Tính toán điều chỉnh đơn giá định giá giữa tài sản mục tiêu và các TSSS (PPSS).
        """
        rules = RulesService(db)
        
        # 1. Chấm điểm tài sản mục tiêu (Target)
        flat_target = flatten_target_asset(data)
        f_target = cls.calculate_f_score(flat_target, rules)
        
        results = []
        target_area = data.land_area
        
        # 2. Chấm điểm từng tài sản so sánh (Comparable) và tính đơn giá điều chỉnh P_tsmt
        for comp_raw in data.ComparableAssets:
            flat_comp = flatten_comparable_asset(comp_raw)
            f_comp = cls.calculate_f_score(flat_comp, rules)
            
            price = comp_raw.Comparable_Transaction.Transaction_Price
            area = comp_raw.Comparable_Property_Detail.Land_Area
            
            p_tsmt = None
            if f_comp != 0 and price and area and target_area:
                p_tsmt = (price * f_target * target_area) / (f_comp * area)
                p_tsmt = round(p_tsmt)
                
            results.append({
                "Comparable_id": comp_raw.Comparable_id,
                "price": price,
                "f_score": f_comp,
                "P_tsmt": p_tsmt
            })
            
        return {
            "target_asset": {
                "PropertyId": data.PropertyId,
                "f_score": f_target
            },
            "Comparable_Assets": results
        }

    @staticmethod
    def calculate_benchmark(data: ValuationInputSchema) -> dict:
        """
        Tính toán các chỉ số thống kê về đơn giá giao dịch của các tài sản so sánh.
        """
        comps = data.ComparableAssets
        p_list = []
        
        for c in comps:
            price = c.Comparable_Transaction.Transaction_Price
            area = c.Comparable_Property_Detail.Land_Area
            if price and area:
                p_list.append(price / area)
                
        # Dump dữ liệu gốc để giữ tính tương thích ngược
        response_data = data.model_dump()
        
        if not p_list:
            response_data["benchmark"] = None
            return response_data
            
        p_min, p_max = min(p_list), max(p_list)
        response_data["benchmark"] = {
            "average":   round(sum(p_list) / len(p_list)),
            "median":    round(statistics.median(p_list)),
            "min":       p_min,
            "max":       p_max,
            "range":     p_max - p_min,
            "n_samples": len(p_list)
        }
        
        return response_data
