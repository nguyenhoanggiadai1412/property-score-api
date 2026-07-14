from sqlalchemy import Column, Integer, String, BigInteger, Float, Text
from app.core.database import Base


class BangGiaDat(Base):
    """Bảng giá đất nhà nước — đơn giá theo vị trí (VT1–VT5)."""
    __tablename__ = "bang_gia_dat"
    __table_args__ = {"schema": "public"}

    STT      = Column(Integer, primary_key=True, nullable=False)
    khu_vuc  = Column(Text, nullable=False)
    duong    = Column(Text, nullable=True)
    doan     = Column(Text, nullable=True)
    VT1      = Column(BigInteger, nullable=True)
    VT2      = Column(BigInteger, nullable=True)
    VT3      = Column(BigInteger, nullable=True)
    VT4      = Column(BigInteger, nullable=True)
    VT5      = Column(BigInteger, nullable=True)
    loai     = Column(Text, nullable=True)


class DepreciationRate(Base):
    """Bảng khấu hao — theo Cấp Nhà."""
    __tablename__ = "depreciation_rate"
    __table_args__ = {"schema": "public"}

    id             = Column(Integer, primary_key=True, autoincrement=True)
    building_grade = Column(String, nullable=False, unique=True)
    rate_per_year  = Column(Float, nullable=False)


class ConstructionUnitPrice(Base):
    """Bảng đơn giá xây dựng (VNĐ/m²) — theo Cấp Nhà + Loại Nhà."""
    __tablename__ = "construction_unit_price"
    __table_args__ = {"schema": "public"}

    id             = Column(Integer, primary_key=True, autoincrement=True)
    building_grade = Column(String, nullable=False)
    property_type  = Column(String, nullable=False)
    unit_price     = Column(BigInteger, nullable=False)
