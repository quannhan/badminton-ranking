from app.database import SessionLocal
from app.models import User
from app.auth import verify_password

db = SessionLocal()

# Test với email bạn vừa nhập
email = "thaiquan251198@gmail.com"
password = "Hongquan1998"

user = db.query(User).filter(User.email == email).first()

if user:
    print(f"User tìm thấy: {user.email}")
    print(f"User ID: {user.user_id}")
    print(f"Full name: {user.full_name}")
    print(f"Password hash: {user.password_hash[:50]}...")
    
    # Test verify password
    is_correct = verify_password(password, user.password_hash)
    print(f"\nPassword '{password}' có đúng không? {is_correct}")
else:
    print(f"Không tìm thấy user với email: {email}")

db.close()
