# =====================================================
# FILE: app/routers/users.py
# =====================================================
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db
import base64
import bcrypt
from PIL import Image
from io import BytesIO

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Đăng ký thành viên mới - Cần admin duyệt"""
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        display_name=user.display_name,
        level='C',  # Mặc định level C
        is_active=False  # Chờ admin duyệt
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Đăng nhập"""
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    print(f"[DEBUG LOGIN] Email: {user_credentials.email}")
    print(f"[DEBUG LOGIN] User found: {user is not None}")
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account pending approval. Please wait for admin to activate your account.")
    
    password_valid = auth.verify_password(user_credentials.password, user.password_hash)
    print(f"[DEBUG LOGIN] Password valid: {password_valid}")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Check user settings for require_password_change
    user_settings = db.query(models.UserSettings).filter(
        models.UserSettings.user_id == user.user_id
    ).first()
    
    require_password_change = user_settings.require_password_change if user_settings else False
    
    access_token = auth.create_access_token(data={"sub": str(user.user_id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "require_password_change": require_password_change
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Lấy thông tin user hiện tại"""
    # Refresh to ensure all columns are loaded
    db.refresh(current_user)
    
    print(f"[DEBUG /me] User ID: {current_user.user_id}")
    print(f"[DEBUG /me] Email: {current_user.email}")
    print(f"[DEBUG /me] Gender: {current_user.gender}")
    print(f"[DEBUG /me] Avatar (first 50): {current_user.avatar[:50] if current_user.avatar else 'None'}")
    
    return current_user

@router.get("/profile/{user_id}", response_model=schemas.UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Xem hồ sơ user khác"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/all", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả users đã được kích hoạt"""
    users = db.query(models.User).filter(
        models.User.is_active == True
    ).order_by(models.User.total_points.desc()).all()
    return users

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload avatar cho user với nén ảnh 30% và resize 300x300"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Read file
    contents = await file.read()
    
    # Validate file size (max 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    try:
        # Open image with Pillow
        image = Image.open(BytesIO(contents))
        
        # Convert RGBA to RGB if needed (for PNG with transparency)
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to max 300x300 (maintain aspect ratio)
        max_size = (300, 300)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compress image to 30% quality
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=30, optimize=True)
        compressed_contents = buffer.getvalue()
        
        # Convert to base64
        base64_image = base64.b64encode(compressed_contents).decode('utf-8')
        avatar_data = f"data:image/jpeg;base64,{base64_image}"
        
        # Update user avatar in database
        current_user.avatar = avatar_data
        db.commit()
        
        return {
            "avatar": avatar_data,
            "message": "Avatar uploaded successfully",
            "original_size": len(contents),
            "compressed_size": len(compressed_contents),
            "compression_ratio": f"{(1 - len(compressed_contents)/len(contents)) * 100:.1f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@router.delete("/delete-avatar")
def delete_avatar(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa avatar của user"""
    current_user.avatar = None
    db.commit()
    
    return {"message": "Avatar deleted successfully"}

@router.post("/forgot-password")
def forgot_password(
    request: schemas.PasswordResetRequestCreate,
    db: Session = Depends(get_db)
):
    """Gửi yêu cầu reset mật khẩu"""
    
    # Kiểm tra email có tồn tại không
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống")
    
    # Kiểm tra xem đã có yêu cầu pending chưa
    existing_request = db.query(models.PasswordResetRequest).filter(
        models.PasswordResetRequest.user_id == user.user_id,
        models.PasswordResetRequest.status == 'PENDING'
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Bạn đã có yêu cầu reset mật khẩu đang chờ xử lý")
    
    # Tạo yêu cầu reset mật khẩu
    reset_request = models.PasswordResetRequest(
        user_id=user.user_id,
        email=user.email
    )
    db.add(reset_request)
    
    # Tạo thông báo cho super admin
    super_admin = db.query(models.User).filter(
        models.User.email == "thaiquan251198@gmail.com"
    ).first()
    
    if super_admin:
        notification = models.Notification(
            user_id=super_admin.user_id,
            type='PASSWORD_RESET_REQUEST',
            message=f'Người dùng {user.display_name} ({user.email}) yêu cầu reset mật khẩu'
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": "Yêu cầu reset mật khẩu đã được gửi đến quản trị viên"}

@router.put("/update-profile")
def update_profile(
    request: schemas.UpdateProfileRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin cá nhân"""
    
    user = db.query(models.User).filter(models.User.user_id == current_user.user_id).first()
    
    if request.display_name:
        user.display_name = request.display_name
    
    if request.email:
        # Kiểm tra email mới có bị trùng không
        existing = db.query(models.User).filter(
            models.User.email == request.email,
            models.User.user_id != current_user.user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
        
        user.email = request.email
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {"message": "Cập nhật thông tin thành công", "user": user}

@router.post("/change-password")
def change_password(
    request: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Đổi mật khẩu"""
    
    user = db.query(models.User).filter(models.User.user_id == current_user.user_id).first()
    
    # Xác thực mật khẩu cũ
    if not bcrypt.checkpw(request.old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")
    
    # Hash mật khẩu mới
    new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password_hash = new_password_hash.decode('utf-8')
    user.updated_at = datetime.utcnow()
    
    # Update user settings to clear require_password_change flag
    user_settings = db.query(models.UserSettings).filter(
        models.UserSettings.user_id == current_user.user_id
    ).first()
    
    if user_settings:
        user_settings.require_password_change = False
        user_settings.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Đổi mật khẩu thành công"}