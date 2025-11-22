# =====================================================
# FILE: app/routers/admin.py
# =====================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .. import models, schemas, auth
from ..database import get_db
from ..utils.scoring import calculate_points
import bcrypt

router = APIRouter(prefix="/admin", tags=["Admin"])

class ResetPointsRequest(BaseModel):
    password: str

@router.get("/pending-users", response_model=List[schemas.UserResponse])
def get_pending_users(
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách user chờ duyệt"""
    pending_users = db.query(models.User).filter(
        models.User.is_active == False
    ).order_by(models.User.created_at.desc()).all()
    
    return pending_users

@router.post("/approve-user/{user_id}")
def approve_user(
    user_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Duyệt tài khoản user"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_active:
        raise HTTPException(status_code=400, detail="User already activated")
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    
    # Create notification
    notification = models.Notification(
        user_id=user.user_id,
        type='ACCOUNT_APPROVED',
        message='Tài khoản của bạn đã được kích hoạt. Bạn có thể đăng nhập ngay bây giờ!'
    )
    db.add(notification)
    
    db.commit()
    
    return {"message": "User approved successfully", "user_id": user_id}

@router.post("/reject-user/{user_id}")
def reject_user(
    user_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Từ chối và xóa tài khoản user"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_active:
        raise HTTPException(status_code=400, detail="Cannot reject activated user")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User rejected and deleted", "user_id": user_id}

@router.post("/create-match", response_model=schemas.MatchReportResponse)
def create_match(
    match_data: schemas.MatchReportCreate,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin tạo kèo mới cho users"""
    
    print(f"[DEBUG CREATE MATCH] match_data: {match_data}")
    print(f"[DEBUG CREATE MATCH] team1_player_ids: {match_data.team1_player_ids}")
    print(f"[DEBUG CREATE MATCH] team2_player_ids: {match_data.team2_player_ids}")
    print(f"[DEBUG CREATE MATCH] winning_team: {match_data.winning_team}")
    
    # Validate match type
    valid_types = ['SINGLES', 'DOUBLES_MEN', 'DOUBLES_WOMEN', 'DOUBLES_MIXED']
    if match_data.match_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid match type")
    
    # Validate player counts
    if match_data.match_type == 'SINGLES':
        if len(match_data.team1_player_ids) != 1 or len(match_data.team2_player_ids) != 1:
            raise HTTPException(status_code=400, detail="Singles requires 1 player per team")
    else:
        if len(match_data.team1_player_ids) != 2 or len(match_data.team2_player_ids) != 2:
            raise HTTPException(status_code=400, detail="Doubles requires 2 players per team")
    
    # Check if winning_team is provided (admin already knows result)
    auto_approve = match_data.winning_team is not None and match_data.winning_team in [1, 2]
    
    # Admin-created matches are always APPROVED (no need for review)
    match_report = models.MatchReport(
        reporter_id=current_admin.user_id,
        match_type=match_data.match_type,
        stake_value=match_data.stake_value,
        status='APPROVED',
        approved_by=current_admin.user_id,
        approved_at=datetime.utcnow(),
        notes=match_data.notes,
        match_video_url=match_data.match_video_url
    )
    db.add(match_report)
    db.commit()
    db.refresh(match_report)
    
    # Add team 1 players
    for player_id in match_data.team1_player_ids:
        if match_data.winning_team is None:
            result = "PENDING"
        elif match_data.winning_team == 1:
            result = "WIN"
        else:
            result = "LOSE"
            
        match_player = models.MatchPlayer(
            match_id=match_report.match_id,
            user_id=player_id,
            team=1,
            result=result
        )
        db.add(match_player)
        
        # If auto-approved, calculate and add points immediately
        if auto_approve:
            points = calculate_points(match_data.stake_value, result)
            match_player.points_earned = points
            
            user = db.query(models.User).filter(models.User.user_id == player_id).first()
            user.total_points += points
            user.last_played_date = datetime.utcnow()
            
            if match_data.match_type == 'SINGLES':
                user.singles_points += points
            else:
                user.doubles_points += points
            
            # Notify player
            notification = models.Notification(
                user_id=player_id,
                type='MATCH_CREATED',
                message=f'Admin đã tạo trận đấu cho bạn. Kết quả: {"THẮNG" if result == "WIN" else "THUA"}. Điểm: {points:+d}'
            )
            db.add(notification)
    
    # Add team 2 players
    for player_id in match_data.team2_player_ids:
        if match_data.winning_team is None:
            result = "PENDING"
        elif match_data.winning_team == 2:
            result = "WIN"
        else:
            result = "LOSE"
            
        match_player = models.MatchPlayer(
            match_id=match_report.match_id,
            user_id=player_id,
            team=2,
            result=result
        )
        db.add(match_player)
        
        # If auto-approved, calculate and add points immediately
        if auto_approve:
            points = calculate_points(match_data.stake_value, result)
            match_player.points_earned = points
            
            user = db.query(models.User).filter(models.User.user_id == player_id).first()
            user.total_points += points
            user.last_played_date = datetime.utcnow()
            
            if match_data.match_type == 'SINGLES':
                user.singles_points += points
            else:
                user.doubles_points += points
            
            # Notify player
            notification = models.Notification(
                user_id=player_id,
                type='MATCH_CREATED',
                message=f'Admin đã tạo trận đấu cho bạn. Kết quả: {"THẮNG" if result == "WIN" else "THUA"}. Điểm: {points:+d}'
            )
            db.add(notification)
    
    db.commit()
    return match_report

@router.get("/pending-matches", response_model=List[schemas.MatchDetailResponse])
def get_pending_matches(
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách trận đấu chờ duyệt"""
    pending = db.query(models.MatchReport).filter(
        models.MatchReport.status == 'PENDING'
    ).order_by(models.MatchReport.created_at.desc()).all()
    
    result = []
    for match in pending:
        # Get reporter info
        reporter = db.query(models.User).filter(models.User.user_id == match.reporter_id).first()
        
        # Get players info
        players = db.query(models.MatchPlayer).filter(
            models.MatchPlayer.match_id == match.match_id
        ).all()
        
        players_info = []
        for p in players:
            user = db.query(models.User).filter(models.User.user_id == p.user_id).first()
            players_info.append({
                "user_id": p.user_id,
                "display_name": user.display_name if user else "Unknown",
                "team": p.team,
                "result": p.result,
                "points_earned": p.points_earned
            })
        
        match_dict = {
            "match_id": match.match_id,
            "reporter_id": match.reporter_id,
            "reporter_name": reporter.display_name if reporter else "Unknown",
            "match_type": match.match_type,
            "stake_value": match.stake_value,
            "status": match.status,
            "admin_notes": match.admin_notes,
            "created_at": match.created_at,
            "approved_at": match.approved_at,
            "players": players_info
        }
        result.append(match_dict)
    
    return result

@router.post("/approve-match/{match_id}")
def approve_match(
    match_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Duyệt trận đấu và cộng điểm"""
    match = db.query(models.MatchReport).filter(
        models.MatchReport.match_id == match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Match already processed")
    
    # Get all players in match
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    # Calculate and update points
    for player in players:
        points = calculate_points(match.stake_value, player.result)
        player.points_earned = points
        
        # Update user's total points
        user = db.query(models.User).filter(
            models.User.user_id == player.user_id
        ).first()
        
        user.total_points += points
        user.last_played_date = datetime.utcnow()
        
        # Update singles or doubles points
        if match.match_type == 'SINGLES':
            user.singles_points += points
        else:
            user.doubles_points += points
        
        # Create notification
        notification = models.Notification(
            user_id=player.user_id,
            type='MATCH_APPROVED',
            message=f'Trận đấu của bạn đã được duyệt! Bạn nhận được {points} điểm.'
        )
        db.add(notification)
    
    # Update match status
    match.status = 'APPROVED'
    match.approved_at = datetime.utcnow()
    match.approved_by = current_admin.user_id
    
    db.commit()
    
    return {"message": "Match rejected successfully", "match_id": match_id}

@router.post("/update-match-result/{match_id}")
def update_match_result(
    match_id: int,
    winning_team: int,
    match_video_url: Optional[str] = None,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật kết quả kèo đấu (dành cho admin)"""
    from ..utils.scoring import calculate_points
    
    # Validate winning_team
    if winning_team not in [1, 2]:
        raise HTTPException(status_code=400, detail="winning_team must be 1 or 2")
    
    # Get match
    match = db.query(models.MatchReport).filter(
        models.MatchReport.match_id == match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != 'APPROVED':
        raise HTTPException(status_code=400, detail="Can only update APPROVED matches")
    
    # Get all players
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    # Check if match already has results (not PENDING)
    has_result = any(p.result != 'PENDING' for p in players)
    if has_result:
        raise HTTPException(status_code=400, detail="Match already has results")
    
    # Update player results and calculate points
    for player in players:
        if player.team == winning_team:
            result = "WIN"
        else:
            result = "LOSE"
        
        player.result = result
        points = calculate_points(match.stake_value, result)
        player.points_earned = points
        
        # Update user points
        user = db.query(models.User).filter(models.User.user_id == player.user_id).first()
        user.total_points += points
        user.last_played_date = datetime.utcnow()
        
        if match.match_type == 'SINGLES':
            user.singles_points += points
        else:
            user.doubles_points += points
        
        # Notify player
        notification = models.Notification(
            user_id=player.user_id,
            type='MATCH_RESULT_UPDATED',
            message=f'Kết quả trận đấu đã được cập nhật! Bạn {"THẮNG" if result == "WIN" else "THUA"}. Điểm: {points:+d}'
        )
        db.add(notification)
    
    # Update video URL if provided
    if match_video_url:
        match.match_video_url = match_video_url
    
    db.commit()
    
    return {"message": "Match result updated successfully", "match_id": match_id}

@router.post("/report-match-result/{match_id}")
def report_match_result(
    match_id: int,
    winning_team: int,
    match_video_url: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """User báo cáo kết quả cho kèo admin đã tạo - chờ admin duyệt"""
    
    # Validate winning_team
    if winning_team not in [1, 2]:
        raise HTTPException(status_code=400, detail="winning_team must be 1 or 2")
    
    # Get match
    match = db.query(models.MatchReport).filter(
        models.MatchReport.match_id == match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != 'APPROVED':
        raise HTTPException(status_code=400, detail="Can only report results for APPROVED matches")
    
    # Check if user is in this match
    user_in_match = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id,
        models.MatchPlayer.user_id == current_user.user_id
    ).first()
    
    if not user_in_match:
        raise HTTPException(status_code=403, detail="You are not in this match")
    
    # Get all players
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    # Check if match already has results
    has_result = any(p.result != 'PENDING' for p in players)
    if has_result:
        raise HTTPException(status_code=400, detail="Match already has results")
    
    # Update player results (but don't calculate points yet - wait for admin approval)
    for player in players:
        if player.team == winning_team:
            player.result = "WIN"
        else:
            player.result = "LOSE"
    
    # Change match status to PENDING for admin review
    match.status = 'PENDING'
    match.admin_notes = f'Kết quả được báo cáo bởi {current_user.display_name}'
    
    # Update video URL if provided
    if match_video_url:
        match.match_video_url = match_video_url
    
    # Notify admin
    admins = db.query(models.User).filter(models.User.is_admin == True).all()
    for admin in admins:
        notification = models.Notification(
            user_id=admin.user_id,
            type='MATCH_RESULT_REPORTED',
            message=f'{current_user.display_name} đã báo cáo kết quả trận đấu #{match_id}. Vui lòng kiểm tra và duyệt.'
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": "Match result reported successfully. Waiting for admin approval.", "match_id": match_id}



@router.post("/reject-match/{match_id}")
def reject_match(
    match_id: int,
    admin_notes: str,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Từ chối trận đấu"""
    match = db.query(models.MatchReport).filter(
        models.MatchReport.match_id == match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Match already processed")
    
    match.status = 'REJECTED'
    match.admin_notes = admin_notes
    match.approved_by = current_admin.user_id
    
    # Notify all players
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    for player in players:
        notification = models.Notification(
            user_id=player.user_id,
            type='MATCH_REJECTED',
            message=f'Trận đấu của bạn đã bị từ chối. Lý do: {admin_notes}'
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": "Match rejected", "match_id": match_id}

@router.post("/reset-all-points")
def reset_all_points(
    request: ResetPointsRequest,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Reset điểm cho tất cả thành viên - chỉ dành cho super admin"""
    
    # Kiểm tra xem có phải super admin không
    SUPER_ADMIN_EMAIL = "thaiquan251198@gmail.com"
    if current_admin.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can reset all points")
    
    # Xác thực mật khẩu
    if not bcrypt.checkpw(request.password.encode('utf-8'), current_admin.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Mật khẩu không đúng")
    
    # Reset điểm cho tất cả user
    users = db.query(models.User).all()
    reset_count = 0
    
    for user in users:
        user.total_points = 0
        user.singles_points = 0
        user.doubles_points = 0
        reset_count += 1
    
    db.commit()
    
    return {
        "message": "All points have been reset successfully",
        "users_affected": reset_count
    }

@router.get("/password-reset-requests")
def get_password_reset_requests(
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách yêu cầu reset mật khẩu - chỉ super admin"""
    
    SUPER_ADMIN_EMAIL = "thaiquan251198@gmail.com"
    if current_admin.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can view password reset requests")
    
    requests = db.query(models.PasswordResetRequest).filter(
        models.PasswordResetRequest.status == 'PENDING'
    ).order_by(models.PasswordResetRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        user = db.query(models.User).filter(models.User.user_id == req.user_id).first()
        result.append({
            "request_id": req.request_id,
            "user_id": req.user_id,
            "email": req.email,
            "display_name": user.display_name if user else "Unknown",
            "status": req.status,
            "created_at": req.created_at
        })
    
    return result

@router.post("/approve-password-reset/{request_id}")
def approve_password_reset(
    request_id: int,
    new_password: str,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Duyệt yêu cầu reset mật khẩu và cấp mật khẩu mới - chỉ super admin"""
    
    SUPER_ADMIN_EMAIL = "thaiquan251198@gmail.com"
    if current_admin.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can approve password reset")
    
    reset_request = db.query(models.PasswordResetRequest).filter(
        models.PasswordResetRequest.request_id == request_id
    ).first()
    
    if not reset_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if reset_request.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Cập nhật mật khẩu user
    user = db.query(models.User).filter(models.User.user_id == reset_request.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash mật khẩu mới
    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password_hash = new_password_hash.decode('utf-8')
    user.updated_at = datetime.utcnow()
    
    # Create or update user settings to set require_password_change flag
    user_settings = db.query(models.UserSettings).filter(
        models.UserSettings.user_id == user.user_id
    ).first()
    
    if user_settings:
        user_settings.require_password_change = True
        user_settings.updated_at = datetime.utcnow()
    else:
        user_settings = models.UserSettings(
            user_id=user.user_id,
            require_password_change=True
        )
        db.add(user_settings)
    
    # Cập nhật trạng thái request
    reset_request.status = 'APPROVED'
    reset_request.new_password = new_password
    reset_request.resolved_at = datetime.utcnow()
    reset_request.resolved_by = current_admin.user_id
    
    # Tạo thông báo cho user
    notification = models.Notification(
        user_id=user.user_id,
        type='PASSWORD_RESET_APPROVED',
        message=f'Mật khẩu của bạn đã được reset. Mật khẩu mới: {new_password}. Vui lòng đổi mật khẩu sau khi đăng nhập.'
    )
    db.add(notification)
    
    db.commit()
    
    return {
        "message": "Password reset approved",
        "new_password": new_password,
        "user_email": user.email
    }

@router.post("/reject-password-reset/{request_id}")
def reject_password_reset(
    request_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Từ chối yêu cầu reset mật khẩu - chỉ super admin"""
    
    SUPER_ADMIN_EMAIL = "thaiquan251198@gmail.com"
    if current_admin.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can reject password reset")
    
    reset_request = db.query(models.PasswordResetRequest).filter(
        models.PasswordResetRequest.request_id == request_id
    ).first()
    
    if not reset_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if reset_request.status != 'PENDING':
        raise HTTPException(status_code=400, detail="Request already processed")
    
    reset_request.status = 'REJECTED'
    reset_request.resolved_at = datetime.utcnow()
    reset_request.resolved_by = current_admin.user_id
    
    # Tạo thông báo cho user
    user = db.query(models.User).filter(models.User.user_id == reset_request.user_id).first()
    if user:
        notification = models.Notification(
            user_id=user.user_id,
            type='PASSWORD_RESET_REJECTED',
            message='Yêu cầu reset mật khẩu của bạn đã bị từ chối. Vui lòng liên hệ quản trị viên.'
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": "Password reset request rejected"}

@router.post("/update-match-video/{match_id}")
def update_match_video(
    match_id: int,
    video_data: dict,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật link YouTube cho trận đấu đã có kết quả"""
    
    # Lấy trận đấu
    match = db.query(models.MatchReport).filter(models.MatchReport.match_id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Kiểm tra trận đấu đã có kết quả chưa
    if match.status != 'APPROVED':
        raise HTTPException(status_code=400, detail="Can only update video for completed matches")
    
    # Cập nhật link video (có thể chứa nhiều link phân cách bởi \n)
    video_url = video_data.get('match_video_url', '').strip()
    match.match_video_url = video_url if video_url else None
    match.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(match)
    
    return {
        "message": "Match video updated successfully",
        "match_id": match_id,
        "match_video_url": match.match_video_url
    }

@router.post("/cancel-match-result/{match_id}")
def cancel_match_result(
    match_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Hủy bỏ kết quả trận đấu và hoàn trả điểm - chỉ super admin"""
    
    # Kiểm tra super admin
    SUPER_ADMIN_EMAIL = "thaiquan251198@gmail.com"
    if current_admin.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can cancel match results")
    
    # Lấy trận đấu
    match = db.query(models.MatchReport).filter(models.MatchReport.match_id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Chỉ có thể hủy trận đấu đã APPROVED
    if match.status != 'APPROVED':
        raise HTTPException(status_code=400, detail="Can only cancel APPROVED matches")
    
    # Lấy tất cả players
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    # Kiểm tra xem trận đấu đã có kết quả chưa
    has_result = any(p.result != 'PENDING' for p in players)
    
    if not has_result:
        raise HTTPException(status_code=400, detail="Match has no results to cancel")
    
    # Hoàn trả điểm cho các players
    for player in players:
        if player.points_earned != 0:
            # Trừ điểm đã cộng
            user = db.query(models.User).filter(models.User.user_id == player.user_id).first()
            
            if user:
                user.total_points -= player.points_earned
                
                if match.match_type == 'SINGLES':
                    user.singles_points -= player.points_earned
                else:
                    user.doubles_points -= player.points_earned
                
                # Tạo thông báo
                notification = models.Notification(
                    user_id=player.user_id,
                    type='MATCH_RESULT_CANCELLED',
                    message=f'Kết quả trận đấu #{match_id} đã bị hủy bởi super admin. Điểm {player.points_earned:+d} đã được hoàn trả.'
                )
                db.add(notification)
        
        # Reset kết quả về PENDING
        player.result = 'PENDING'
        player.points_earned = 0
    
    # Xóa video URL (optional - có thể giữ lại)
    # match.match_video_url = None
    
    match.updated_at = datetime.utcnow()
    match.admin_notes = f'Kết quả đã bị hủy bởi super admin {current_admin.display_name} vào {datetime.utcnow()}'
    
    db.commit()
    
    return {
        "message": "Match result cancelled successfully. Points have been refunded.",
        "match_id": match_id,
        "players_affected": len(players)
    }

@router.delete("/delete-match/{match_id}")
def delete_match(
    match_id: int,
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Xóa trận đấu - tất cả admin có quyền"""
    
    # Lấy trận đấu
    match = db.query(models.MatchReport).filter(models.MatchReport.match_id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Lấy tất cả players
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()
    
    # Kiểm tra nếu trận đấu đã APPROVED và có kết quả, cần hoàn trả điểm
    if match.status == 'APPROVED':
        has_result = any(p.result != 'PENDING' for p in players)
        
        if has_result:
            # Hoàn trả điểm cho các players
            for player in players:
                if player.points_earned != 0:
                    user = db.query(models.User).filter(models.User.user_id == player.user_id).first()
                    
                    if user:
                        user.total_points -= player.points_earned
                        
                        if match.match_type == 'SINGLES':
                            user.singles_points -= player.points_earned
                        else:
                            user.doubles_points -= player.points_earned
                        
                        # Tạo thông báo
                        notification = models.Notification(
                            user_id=player.user_id,
                            type='MATCH_DELETED',
                            message=f'Trận đấu #{match_id} đã bị xóa bởi admin. Điểm {player.points_earned:+d} đã được hoàn trả.'
                        )
                        db.add(notification)
        else:
            # Trận chưa có kết quả, chỉ thông báo
            for player in players:
                notification = models.Notification(
                    user_id=player.user_id,
                    type='MATCH_DELETED',
                    message=f'Trận đấu #{match_id} đã bị hủy bởi admin.'
                )
                db.add(notification)
    
    # Xóa match_players trước (foreign key constraint)
    for player in players:
        db.delete(player)
    
    # Xóa match_report
    db.delete(match)
    
    db.commit()
    
    return {
        "message": "Match deleted successfully",
        "match_id": match_id,
        "status": match.status,
        "players_affected": len(players)
    }


