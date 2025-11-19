from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    display_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    user_id: int
    gender: Optional[str]
    avatar: Optional[str]
    level: str
    total_points: int
    singles_points: int
    doubles_points: int
    last_played_date: Optional[datetime]
    is_admin: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    require_password_change: bool = False

class MatchReportCreate(BaseModel):
    match_type: str  # SINGLES, DOUBLES_MEN, DOUBLES_WOMEN, DOUBLES_MIXED
    stake_value: int
    team1_player_ids: List[int]  # 1 player for singles, 2 for doubles
    team2_player_ids: List[int]
    winning_team: Optional[int] = None  # 1 or 2, optional (None if match not played yet)
    notes: Optional[str] = None  # User notes/comments
    match_video_url: Optional[str] = None  # YouTube or video link

class MatchPlayerInfo(BaseModel):
    user_id: int
    display_name: str
    team: int
    result: str
    points_earned: int
    
    class Config:
        from_attributes = True

class MatchReportResponse(BaseModel):
    match_id: int
    reporter_id: int
    reporter_name: Optional[str] = None
    match_type: str
    stake_value: int
    status: str
    admin_notes: Optional[str] = None
    notes: Optional[str] = None
    match_video_url: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchDetailResponse(MatchReportResponse):
    players: List[dict] = []  # Will be populated manually
    
    class Config:
        from_attributes = True

class RankingResponse(BaseModel):
    user_id: int
    display_name: str
    level: str
    points: int
    rank: int
    
    class Config:
        from_attributes = True

class PasswordResetRequestCreate(BaseModel):
    email: EmailStr

class PasswordResetRequestResponse(BaseModel):
    request_id: int
    user_id: int
    email: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str