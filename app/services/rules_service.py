from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session, joinedload
from app.models.lookup import LookupFeature, LookupValue

class RulesService:
    def __init__(self, db: Session):
        self.weights: Dict[str, float] = {}
        # feature_code -> [(min_val, max_val, score)]
        self.numeric_rules: Dict[str, List[Tuple[Optional[float], Optional[float], float]]] = {}
        # feature_code -> {text_lower: score}
        self.category_rules: Dict[str, Dict[str, float]] = {}
        self._load_rules(db)

    def _load_rules(self, db: Session):
        # Truy vấn toàn bộ feature kèm values sử dụng joinedload để tránh N+1 queries
        features = db.query(LookupFeature).options(joinedload(LookupFeature.values)).all()
        
        for f in features:
            self.weights[f.feature_code] = float(f.weight) if f.weight is not None else 0.0
            
            num_rules = []
            cat_rules = {}
            has_cat = False
            
            for val in f.values:
                if val.text_value is not None:
                    has_cat = True
                    cat_rules[str(val.text_value).strip().lower()] = float(val.score) if val.score is not None else 0.0
                else:
                    min_v = float(val.min_value) if val.min_value is not None else None
                    max_v = float(val.max_value) if val.max_value is not None else None
                    score_v = float(val.score) if val.score is not None else 0.0
                    num_rules.append((min_v, max_v, score_v))
            
            if has_cat:
                self.category_rules[f.feature_code] = cat_rules
            if num_rules:
                # Sắp xếp giảm dần theo min_value để so khớp từ ngưỡng cao nhất trước
                num_rules.sort(key=lambda x: (x[0] if x[0] is not None else float("-inf")), reverse=True)
                self.numeric_rules[f.feature_code] = num_rules

    def get_feature_score(self, feature_code: str, value: Any) -> float:
        """
        Tính toán điểm số (k) cho thuộc tính cụ thể. Trả về 0.0 nếu dữ liệu trống hoặc không khớp.
        """
        if value is None:
            return 0.0

        # 1. So khớp Rule số (Numeric)
        if feature_code in self.numeric_rules:
            try:
                v = float(value)
            except (ValueError, TypeError):
                return 0.0
            for min_v, max_v, score in self.numeric_rules[feature_code]:
                lower_ok = (min_v is None) or (v >= min_v)
                upper_ok = (max_v is None) or (v < max_v)
                if lower_ok and upper_ok:
                    return score
            return 0.0

        # 2. So khớp Rule chữ (Categorical)
        if feature_code in self.category_rules:
            normalized_val = str(value).strip().lower()
            return self.category_rules[feature_code].get(normalized_val, 0.0)

        return 0.0

    def calculate_weighted_score(self, feature_code: str, value: Any) -> float:
        """
        Trả về kết quả có trọng số: k * weight
        """
        k = self.get_feature_score(feature_code, value)
        weight = self.weights.get(feature_code, 0.0)
        return k * weight

    def get_all_features(self) -> List[str]:
        return list(self.weights.keys())
