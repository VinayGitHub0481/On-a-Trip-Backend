from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.faq import FAQCreate, FAQUpdate, FAQOut
from app.services import faq_service
from app.core.deps import require_admin_or_creator
from app.models.user import User

router = APIRouter(prefix="/faqs", tags=["FAQs"])


@router.get("", response_model=list[dict])
def list_faqs(db: Session = Depends(get_db)):
    return faq_service.get_all_faqs(db)


@router.post("/admin", response_model=FAQOut)
def create(
    payload: FAQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_creator),
):
    return faq_service.create_faq(db, payload, current_user.id)


@router.put(
    "/admin/{item_id}",
    response_model=FAQOut,
    dependencies=[Depends(require_admin_or_creator)],
)
def update(item_id: int, payload: FAQUpdate, db: Session = Depends(get_db)):
    return faq_service.update_faq(db, item_id, payload)


@router.delete(
    "/admin/{item_id}",
    status_code=204,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete(item_id: int, db: Session = Depends(get_db)):
    faq_service.delete_faq(db, item_id)
