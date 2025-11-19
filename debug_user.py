"""
Script để debug user trong database
"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models import User
from app.auth import verify_password
import json

db = SessionLocal()

# Test với email bạn vừa nhập
email = "thaiquan251198@gmail.com"
password = "Hongquan1998"

user = db.query(User).filter(User.email == email).first()

if user:
    print(f"✓ User tìm thấy: {user.email}")
    print(f"  User ID: {user.user_id}")
    print(f"  Full name: {user.display_name}")
    print(f"  Gender: {user.gender}")
    print(f"  Avatar (first 100 chars): {user.avatar[:100] if user.avatar else 'None'}")
    print(f"  Level: {user.level}")
    print(f"  Is admin: {user.is_admin}")
    
    # Test verify password
    is_correct = verify_password(password, user.password_hash)
    print(f"\n{'✓' if is_correct else '✗'} Password '{password}' {'đúng' if is_correct else 'SAI'}")
    
    # Export as JSON như API response
    print("\n=== JSON Response (như API trả về) ===")
    user_dict = {
        "user_id": user.user_id,
        "email": user.email,
        "display_name": user.display_name,
        "gender": user.gender,
        "avatar": user.avatar[:100] + "..." if user.avatar else None,
        "level": user.level,
        "total_points": user.total_points,
        "singles_points": user.singles_points,
        "doubles_points": user.doubles_points,
        "last_played_date": str(user.last_played_date) if user.last_played_date else None,
        "is_admin": user.is_admin
    }
    print(json.dumps(user_dict, indent=2))
else:
    print(f"✗ Không tìm thấy user với email: {email}")
    print("\nDanh sách các user trong DB:")
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email} (ID: {u.user_id}, Name: {u.display_name})")

db.close()
