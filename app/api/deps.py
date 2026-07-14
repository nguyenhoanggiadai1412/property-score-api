from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db

# Dependency alias hoặc các dependency chung khác có thể định nghĩa ở đây
# Ví dụ: kiểm tra API Key, OAuth2 token, ...
