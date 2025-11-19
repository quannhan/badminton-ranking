# =====================================================
# FILE: app/routers/matches.py
# =====================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .. import models, schemas, auth
from ..database import get_db
from ..utils.scoring import calculate_points

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/report", response_model=schemas.MatchReportResponse)
def report_match(
    match_data: schemas.MatchReportCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Báo cáo trận đấu"""
    
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
    
    # Create match report
    match_report = models.MatchReport(
        reporter_id=current_user.user_id,
        match_type=match_data.match_type,
        stake_value=match_data.stake_value,
        status='PENDING',
        notes=match_data.notes,
        match_video_url=match_data.match_video_url
    )
    db.add(match_report)
    db.commit()
    db.refresh(match_report)
    
    # Add team 1 players
    for player_id in match_data.team1_player_ids:
        result = "WIN" if match_data.winning_team == 1 else "LOSE"
        match_player = models.MatchPlayer(
            match_id=match_report.match_id,
            user_id=player_id,
            team=1,
            result=result
        )
        db.add(match_player)
    
    # Add team 2 players
    for player_id in match_data.team2_player_ids:
        result = "WIN" if match_data.winning_team == 2 else "LOSE"
        match_player = models.MatchPlayer(
            match_id=match_report.match_id,
            user_id=player_id,
            team=2,
            result=result
        )
        db.add(match_player)
    
    db.commit()
    
    # Create notifications for all players
    all_player_ids = match_data.team1_player_ids + match_data.team2_player_ids
    for player_id in all_player_ids:
        if player_id != current_user.user_id:
            notification = models.Notification(
                user_id=player_id,
                type='MATCH_REPORTED',
                message=f'{current_user.display_name} đã báo cáo một trận đấu có bạn tham gia. Đang chờ Admin duyệt.'
            )
            db.add(notification)
    
    db.commit()
    return match_report

@router.get("/my-matches", response_model=List[schemas.MatchDetailResponse])
def get_my_matches(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử trận đấu của tôi"""
    matches = db.query(models.MatchReport).join(
        models.MatchPlayer
    ).filter(
        models.MatchPlayer.user_id == current_user.user_id
    ).order_by(models.MatchReport.created_at.desc()).all()
    
    result = []
    for match in matches:
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

@router.get("/all", response_model=List[schemas.MatchDetailResponse])
def get_all_matches(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lấy tất cả trận đấu (cho dashboard)"""
    matches = db.query(models.MatchReport).order_by(
        models.MatchReport.created_at.desc()
    ).limit(50).all()
    
    result = []
    for match in matches:
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
            "notes": match.notes,
            "match_video_url": match.match_video_url,
            "created_at": match.created_at,
            "approved_at": match.approved_at,
            "players": players_info
        }
        result.append(match_dict)
    
    return result

@router.get("/completed-this-month", response_model=List[schemas.MatchDetailResponse])
def get_completed_matches_this_month(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lấy các trận đấu đã có kết quả (APPROVED + có WIN/LOSE) trong tháng hiện tại"""
    from datetime import datetime
    
    # Get first day of current month
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    
    matches = db.query(models.MatchReport).filter(
        models.MatchReport.status == 'APPROVED',
        models.MatchReport.created_at >= first_day
    ).order_by(models.MatchReport.created_at.desc()).all()
    
    result = []
    for match in matches:
        # Get players to check if match has results
        players = db.query(models.MatchPlayer).filter(
            models.MatchPlayer.match_id == match.match_id
        ).all()
        
        # Only include matches that have actual results (not PENDING)
        has_result = any(p.result != 'PENDING' for p in players)
        if not has_result:
            continue
        
        # Get reporter info
        reporter = db.query(models.User).filter(models.User.user_id == match.reporter_id).first()
        
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
            "notes": match.notes,
            "match_video_url": match.match_video_url,
            "created_at": match.created_at,
            "approved_at": match.approved_at,
            "players": players_info
        }
        result.append(match_dict)
    
    return result

@router.get("/pending-this-month", response_model=List[schemas.MatchDetailResponse])
def get_pending_matches_this_month(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lấy các kèo đấu chưa hoàn tất trong tháng hiện tại - tạo bởi admin (bao gồm cả đang chờ duyệt)"""
    from datetime import datetime
    
    # Get first day of current month
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    
    # Get admin users
    admins = db.query(models.User).filter(models.User.is_admin == True).all()
    admin_ids = [admin.user_id for admin in admins]
    
    matches = db.query(models.MatchReport).filter(
        models.MatchReport.reporter_id.in_(admin_ids),
        models.MatchReport.created_at >= first_day
    ).order_by(models.MatchReport.created_at.desc()).all()
    
    result = []
    for match in matches:
        # Get players to check match status
        players = db.query(models.MatchPlayer).filter(
            models.MatchPlayer.match_id == match.match_id
        ).all()
        
        # Include matches that:
        # 1. Status = APPROVED and all results are PENDING (not yet played)
        # 2. Status = PENDING (reported, waiting for admin approval)
        # Exclude: Status = APPROVED with WIN/LOSE results (already completed)
        
        has_result = any(p.result != 'PENDING' for p in players)
        
        if match.status == 'APPROVED' and has_result:
            # This match is completed, skip it
            continue
        
        # Get reporter info
        reporter = db.query(models.User).filter(models.User.user_id == match.reporter_id).first()
        
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
            "notes": match.notes,
            "match_video_url": match.match_video_url,
            "created_at": match.created_at,
            "approved_at": match.approved_at,
            "players": players_info
        }
        result.append(match_dict)
    
    return result
