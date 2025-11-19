from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Kết nối Supabase thành công!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test query tables
        result = connection.execute(text("SELECT COUNT(*) FROM users;"))
        count = result.fetchone()
        print(f"✅ Số users trong database: {count[0]}")
        
except Exception as e:
    print(f"❌ Lỗi kết nối: {e}")