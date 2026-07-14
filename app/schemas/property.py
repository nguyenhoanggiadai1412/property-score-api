from pydantic import BaseModel, Field, AliasChoices
from typing import List, Optional, Dict

class BuildingInfoSchema(BaseModel):
    TotalFloorArea: Optional[float] = 0.0
    ConstructionArea: Optional[float] = 0.0
    NumberOfFloors: Optional[int] = 0
    ConstructionYear: Optional[int] = None

class ComparablePropertyDetailSchema(BaseModel):
    Land_Area: Optional[float] = 0.0
    Frontage: Optional[float] = 0.0
    Road_width: Optional[float] = 0.0
    Building_Area: Optional[float] = 0.0

class ComparableTransactionSchema(BaseModel):
    Transaction_Price: Optional[float] = None
    Transaction_Date: Optional[str] = None

class ComparableDistanceSchema(BaseModel):
    DistanceM: Optional[float] = None

class ComparableAssetSchema(BaseModel):
    Comparable_id: str
    Comparable_Property_Detail: ComparablePropertyDetailSchema
    Comparable_Transaction: ComparableTransactionSchema
    Advantages: Optional[Dict[str, Optional[float]]] = Field(default_factory=dict)
    Comparable_Distances: Optional[List[ComparableDistanceSchema]] = Field(default_factory=list)
    data_source: Optional[str] = None

    class Config:
        extra = "allow"

class ValuationInputSchema(BaseModel):
    PropertyId: str
    PropertyType: Optional[str] = None
    RoadAccessType: Optional[str] = None
    RoadWidth: Optional[float] = None
    frontage_count: Optional[int] = None
    distance_to_main_road: Optional[float] = None
    Construction_Area: Optional[float] = None
    BuildingInfo: Optional[BuildingInfoSchema] = None
    Advantages: Optional[Dict[str, Optional[float]]] = Field(default_factory=dict)
    land_area: Optional[float] = None
    frontage_width: Optional[float] = None
    ComparableAssets: List[ComparableAssetSchema] = Field(
        default_factory=list, 
        validation_alias=AliasChoices(
            "Comparable_Assets",
            "ComparableAssets"
        ))

    class Config:
        extra = "allow"
