# =====================================================
# FILE: app/routers/rankings.py
# =====================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/rankings", tags=["Rankings"])

@router.get("/overall/{level}", response_model=List[schemas.RankingResponse])
def get_overall_rankings(level: str, db: Session = Depends(get_db)):
    """Bảng xếp hạng tổng theo level"""
    if level not in ['A', 'B', 'C', 'D', 'ALL']:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    query = db.query(
        models.User.user_id,
        models.User.display_name,
        models.User.level,
        models.User.total_points
    )
    
    if level != 'ALL':
        query = query.filter(models.User.level == level)
    
    users = query.order_by(desc(models.User.total_points)).all()
    
    rankings = []
    for rank, user in enumerate(users, start=1):
        rankings.append({
            "user_id": user.user_id,
            "display_name": user.display_name,
            "level": user.level,
            "points": user.total_points,
            "rank": rank
        })
    
    return rankings

@router.get("/{match_type}/{level}", response_model=List[schemas.RankingResponse])
def get_specific_rankings(match_type: str, level: str, db: Session = Depends(get_db)):
    """Bảng xếp hạng theo loại trận (Đơn/Đôi) và level"""
    valid_types = ['SINGLES', 'DOUBLES_MEN', 'DOUBLES_WOMEN', 'DOUBLES_MIXED']
    if match_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid match type")
    
    if level not in ['A', 'B', 'C', 'D', 'ALL']:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    # Get current month
    current_month = datetime.now().strftime("%Y-%m")
    
    # Query rankings
    query = db.query(models.Ranking).filter(
        models.Ranking.ranking_type == match_type,
        models.Ranking.month_year == current_month
    )
    
    if level != 'ALL':
        query = query.filter(models.Ranking.level == level)
    
    rankings = query.order_by(models.Ranking.rank).all()
    
    # If no rankings for current month, create from user data
    if not rankings:
        if level == 'ALL':
            # Create rankings for all levels
            result = []
            for lvl in ['A', 'B', 'C']:
                result.extend(_create_monthly_rankings(db, match_type, lvl, current_month))
            # Re-sort by points for combined view
            result.sort(key=lambda x: x['points'], reverse=True)
            # Re-rank
            for rank, item in enumerate(result, start=1):
                item['rank'] = rank
            return result
        else:
            return _create_monthly_rankings(db, match_type, level, current_month)
    
    # Convert to response format
    result = []
    for ranking in rankings:
        user = db.query(models.User).filter(
            models.User.user_id == ranking.user_id
        ).first()
        
        result.append({
            "user_id": user.user_id,
            "display_name": user.display_name,
            "level": ranking.level,
            "points": ranking.points,
            "rank": ranking.rank
        })
    
    # If level is ALL, re-sort and re-rank combined results
    if level == 'ALL' and result:
        result.sort(key=lambda x: x['points'], reverse=True)
        for rank, item in enumerate(result, start=1):
            item['rank'] = rank
    
    return result

def _create_monthly_rankings(db: Session, match_type: str, level: str, month_year: str):
    """Tạo bảng xếp hạng tháng mới từ dữ liệu users"""
    # Get points field based on match type
    if match_type == 'SINGLES':
        points_field = models.User.singles_points
    else:
        points_field = models.User.doubles_points
    
    users = db.query(models.User).filter(
        models.User.level == level
    ).order_by(desc(points_field)).all()
    
    result = []
    for rank, user in enumerate(users, start=1):
        points = user.singles_points if match_type == 'SINGLES' else user.doubles_points
        
        # Create ranking record
        ranking = models.Ranking(
            user_id=user.user_id,
            ranking_type=match_type,
            level=level,
            points=points,
            rank=rank,
            month_year=month_year
        )
        db.add(ranking)
        
        result.append({
            "user_id": user.user_id,
            "display_name": user.display_name,
            "level": level,
            "points": points,
            "rank": rank
        })
    
    db.commit()
    return result

@router.post("/reset-monthly")
def reset_monthly_rankings(
    current_admin: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Reset bảng xếp hạng hàng tháng (Chạy đầu tháng)"""
    current_month = datetime.now().strftime("%Y-%m")
    
    # Create new rankings for all types and levels
    match_types = ['SINGLES', 'DOUBLES_MEN', 'DOUBLES_WOMEN', 'DOUBLES_MIXED']
    levels = ['A', 'B', 'C', 'D']
    
    for match_type in match_types:
        for level in levels:
            _create_monthly_rankings(db, match_type, level, current_month)
    
    return {"message": "Monthly rankings reset successfully", "month": current_month}