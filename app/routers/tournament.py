from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/tournament", tags=["tournament"])

# Super admin email
SUPER_ADMIN_EMAIL = 'thaiquan251198@gmail.com'

class TournamentRulesResponse(BaseModel):
    rules: Optional[str] = None
    updated_at: Optional[str] = None

class TournamentRulesUpdate(BaseModel):
    rules: str

@router.get("/rules", response_model=TournamentRulesResponse)
async def get_tournament_rules(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get tournament rules (public for all authenticated users)"""
    tournament = db.query(models.TournamentSettings).first()
    
    if not tournament or not tournament.rules:
        return {"rules": None, "updated_at": None}
    
    return {
        "rules": tournament.rules,
        "updated_at": tournament.updated_at.isoformat() if tournament.updated_at else None
    }

@router.post("/rules", response_model=TournamentRulesResponse)
async def update_tournament_rules(
    rules_data: TournamentRulesUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update tournament rules (super admin only)"""
    # Check if user is super admin
    if current_user.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Only super admin can update tournament rules")
    
    # Get or create tournament settings
    tournament = db.query(models.TournamentSettings).first()
    
    if not tournament:
        tournament = models.TournamentSettings(
            rules=rules_data.rules,
            updated_at=datetime.utcnow(),
            updated_by=current_user.user_id
        )
        db.add(tournament)
    else:
        tournament.rules = rules_data.rules
        tournament.updated_at = datetime.utcnow()
        tournament.updated_by = current_user.user_id
    
    db.commit()
    db.refresh(tournament)
    
    return {
        "rules": tournament.rules,
        "updated_at": tournament.updated_at.isoformat() if tournament.updated_at else None
    }
