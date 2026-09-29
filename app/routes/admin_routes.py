from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserOut, UserUpdateStatus
from app.services import auth_service
from app.core.deps import require_admin
from app.models.user import User

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)]
)


@router.get("/creators", response_model=list[UserOut])
def list_creators(db: Session = Depends(get_db)):
    return auth_service.list_creators(db)


@router.patch("/creators/{user_id}/status", response_model=UserOut)
def set_status(user_id: int, payload: UserUpdateStatus, db: Session = Depends(get_db)):
    """Enable/disable a content creator's access without deleting their account."""
    return auth_service.set_user_active_status(db, user_id, payload.is_active)


@router.delete("/creators/{user_id}", status_code=204)
def remove_creator(user_id: int, db: Session = Depends(get_db)):
    auth_service.delete_user(db, user_id)
