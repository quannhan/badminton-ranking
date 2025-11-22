# =====================================================
# FILE: app/main.py
# =====================================================
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .database import get_db
from .routers import users, matches, admin, rankings
from . import models
from .utils.email import send_inactive_warning
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Badminton Club Management API",
    description="API for managing badminton club members, matches, and rankings",
    version="1.0.0"
)

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:4200",
        "https://badminton-frontend-l51wvcek9-quan-thais-projects-5e8ad6f4.vercel.app",
        "https://badminton-frontend-rosy.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(matches.router)
app.include_router(admin.router)
app.include_router(rankings.router)
from .routers import tournament
app.include_router(tournament.router)

@app.get("/")
def root():
    return {
        "message": "Badminton Club Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/cron/send-inactive-warnings")
def send_inactive_warnings_cron(db: Session = Depends(get_db)):
    """
    Cron job: Gửi email cảnh báo cho người chơi không hoạt động
    Chạy hàng tuần hoặc hàng tháng
    """
    inactive_threshold_days = int(os.getenv("INACTIVE_DAYS_THRESHOLD", 30))
    threshold_date = datetime.utcnow() - timedelta(days=inactive_threshold_days)
    
    # Find inactive users
    inactive_users = db.query(models.User).filter(
        models.User.last_played_date < threshold_date,
        models.User.is_admin == False
    ).all()
    
    sent_count = 0
    for user in inactive_users:
        days_inactive = (datetime.utcnow() - user.last_played_date).days
        
        # Send email
        success = send_inactive_warning(
            user.email,
            user.display_name,
            days_inactive
        )
        
        if success:
            # Create notification
            notification = models.Notification(
                user_id=user.user_id,
                type='INACTIVE_WARNING',
                message=f'Bạn đã không chơi trong {days_inactive} ngày. Hãy quay lại sân!'
            )
            db.add(notification)
            sent_count += 1
    
    db.commit()
    
    return {
        "message": f"Sent {sent_count} inactive warnings",
        "threshold_days": inactive_threshold_days
    }

@app.get("/notifications/my")
def get_my_notifications(
    current_user: models.User = Depends(users.auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông báo của tôi"""
    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.user_id
    ).order_by(models.Notification.created_at.desc()).limit(20).all()
    
    return notifications

@app.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: models.User = Depends(users.auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Đánh dấu đã đọc thông báo"""
    notification = db.query(models.Notification).filter(
        models.Notification.notification_id == notification_id,
        models.Notification.user_id == current_user.user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
        return {"message": "Notification marked as read"}
    
    return {"error": "Notification not found"}


# =====================================================
# FILE: requirements.txt
# =====================================================
"""
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic-settings==2.1.0
python-dotenv==1.0.0
supabase==2.3.0
"""


# =====================================================
# HOW TO RUN THE APPLICATION
# =====================================================
"""
1. Install dependencies:
   pip install -r requirements.txt

2. Setup Supabase:
   - Go to https://supabase.com
   - Create free project
   - Get DATABASE_URL from Settings > Database
   - Run the SQL schema in SQL Editor

3. Configure .env file with your credentials

4. Run the application:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

5. Access API documentation:
   http://localhost:8000/docs

6. Setup Cron Job for inactive warnings:
   Add to crontab (Linux/Mac):
   0 9 * * 0 curl -X POST http://localhost:8000/cron/send-inactive-warnings
   
   Or use a cron service like:
   - Render.com Cron Jobs (Free)
   - GitHub Actions (Free)
   - Vercel Cron (Free)

API ENDPOINTS:

Authentication:
- POST /users/register - Register new user
- POST /users/login - Login
- GET /users/me - Get current user profile
- GET /users/profile/{user_id} - View user profile

Matches:
- POST /matches/report - Report match result
- GET /matches/my-matches - Get my match history

Admin:
- GET /admin/pending-matches - View pending matches
- POST /admin/approve-match/{match_id} - Approve match
- POST /admin/reject-match/{match_id} - Reject match

Rankings:
- GET /rankings/overall/{level} - Overall rankings by level (A/B/C)
- GET /rankings/{match_type}/{level} - Rankings by type and level
  match_type: SINGLES, DOUBLES_MEN, DOUBLES_WOMEN, DOUBLES_MIXED
- POST /rankings/reset-monthly - Reset monthly rankings (Admin only)

Notifications:
- GET /notifications/my - Get my notifications
- POST /notifications/{id}/read - Mark as read

System:
- GET / - API info
- GET /health - Health check
- POST /cron/send-inactive-warnings - Send inactive warnings (Cron)

TESTING:
1. Register users at different levels
2. Login to get access token
3. Report matches
4. Admin approves matches
5. Check rankings
6. Test inactive warnings
"""