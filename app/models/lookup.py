from sqlalchemy import Column, String, Numeric, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class LookupFeature(Base):
    __tablename__ = "lookup_feature"
    __table_args__ = {"schema": "public"}

    feature_code = Column(String(100), primary_key=True, nullable=False)
    feature_name = Column(String(255), nullable=True)
    weight = Column(Numeric(10, 4), nullable=True)

    # Thiết lập quan hệ với LookupValue
    values = relationship("LookupValue", back_populates="feature", cascade="all, delete-orphan")

class LookupValue(Base):
    __tablename__ = "lookup_value"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_code = Column(String(100), ForeignKey("public.lookup_feature.feature_code"), nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    text_value = Column(String(255), nullable=True)
    score = Column(Float, nullable=True)

    # Thiết lập quan hệ ngược lại với LookupFeature
    feature = relationship("LookupFeature", back_populates="values")
