from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine with PostgreSQL connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Tự động kiểm tra trạng thái kết nối
)

# Khởi tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Lớp cơ sở cho các mô hình ORM
Base = declarative_base()

# Dependency cung cấp session kết nối cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
