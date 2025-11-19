# =====================================================
# FILE: app/models.py
# =====================================================
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    gender = Column(String(1))  # 'M' for Male, 'F' for Female
    avatar = Column(String)  # URL or path to avatar image
    level = Column(String(1), default='C')
    total_points = Column(Integer, default=0)
    singles_points = Column(Integer, default=0)
    doubles_points = Column(Integer, default=0)
    last_played_date = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)  # Requires admin approval
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    require_password_change = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class MatchReport(Base):
    __tablename__ = "match_reports"
    
    match_id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    match_type = Column(String, nullable=False)
    stake_value = Column(Integer, nullable=False)
    status = Column(String, default='PENDING')
    admin_notes = Column(Text)
    notes = Column(Text)  # User notes/comments
    match_video_url = Column(String)  # YouTube or video link
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.user_id'))
    
    players = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")

class MatchPlayer(Base):
    __tablename__ = "match_players"
    
    match_player_id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('match_reports.match_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    team = Column(Integer, nullable=False)
    result = Column(String, nullable=False)
    points_earned = Column(Integer, default=0)
    
    match = relationship("MatchReport", back_populates="players")

class Ranking(Base):
    __tablename__ = "rankings"
    
    ranking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    ranking_type = Column(String, nullable=False)
    level = Column(String(1), nullable=False)
    points = Column(Integer, default=0)
    rank = Column(Integer)
    month_year = Column(String(7))
    updated_at = Column(DateTime, default=datetime.utcnow)

class PromotionMatch(Base):
    __tablename__ = "promotion_matches"
    
    promotion_id = Column(Integer, primary_key=True, index=True)
    month_year = Column(String(7), nullable=False)
    match_type = Column(String, nullable=False)
    from_level = Column(String(1))
    to_level = Column(String(1))
    player_ids = Column(ARRAY(Integer))
    winner_ids = Column(ARRAY(Integer))
    match_date = Column(DateTime)
    status = Column(String, default='SCHEDULED')
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"
    
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, default='PENDING')  # PENDING, APPROVED, REJECTED
    new_password = Column(String)  # Temporary password set by admin
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.user_id'))