from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.enquiry import (
    EnquiryCreate,
    EnquiryResponse,
)
from app.services.enquiry_service import (
    create_enquiry,
    get_all_enquiries,
    get_enquiry_by_id,
    delete_enquiry,
)
from app.core.deps import require_admin_or_creator

router = APIRouter(
    prefix="/enquiries",
    tags=["Enquiries"],
)


# =========================================================
# PUBLIC - CUSTOMER SUBMITS ENQUIRY
# =========================================================


@router.post(
    "",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_enquiry(
    enquiry_data: EnquiryCreate,
    db: Session = Depends(get_db),
):
    return create_enquiry(
        db=db,
        enquiry_data=enquiry_data,
    )


# =========================================================
# ADMIN - GET ALL ENQUIRIES
# =========================================================


@router.get(
    "/admin",
    response_model=list[EnquiryResponse],
    dependencies=[Depends(require_admin_or_creator)],
)
def get_admin_enquiries(
    db: Session = Depends(get_db),
):
    return get_all_enquiries(db)


# =========================================================
# ADMIN - GET SINGLE ENQUIRY
# =========================================================


@router.get(
    "/admin/{enquiry_id}",
    response_model=EnquiryResponse,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_admin_enquiry(
    enquiry_id: int,
    db: Session = Depends(get_db),
):
    enquiry = get_enquiry_by_id(
        db=db,
        enquiry_id=enquiry_id,
    )

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found",
        )

    return enquiry


# =========================================================
# ADMIN - DELETE ENQUIRY
# =========================================================


@router.delete(
    "/admin/{enquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_admin_enquiry(
    enquiry_id: int,
    db: Session = Depends(get_db),
):
    enquiry = delete_enquiry(
        db=db,
        enquiry_id=enquiry_id,
    )

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found",
        )

    return None
