

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyOut

from app.services import policy_service

from app.core.deps import require_admin_or_creator

from app.models.user import User

router = APIRouter(
prefix="/policies",
tags=["Policy"],
)

@router.get(
"",
response_model=list[dict],
)
def list_policies(
db: Session = Depends(get_db),
):
    return policy_service.get_all_policies(db)

@router.get(
"/{policy_id}",
response_model=dict,
)
def get_policy(
policy_id: int,
db: Session = Depends(get_db),
):
    return policy_service.get_policy(db, policy_id)

@router.get(
"/admin/all",
response_model=list[PolicyOut],
dependencies=[Depends(require_admin_or_creator)],
)
def list_all_policies(
db: Session = Depends(get_db),
):
    return policy_service.get_all_policies(db)


@router.post(
"/admin",
response_model=PolicyOut,
)
def create_policy(
payload: PolicyCreate,
db: Session = Depends(get_db),
current_user: User = Depends(require_admin_or_creator),
):
    return policy_service.create_policy(
    db,
    payload,
    current_user.id,
    )


@router.put(
"/admin/{policy_id}",
response_model=PolicyOut,
dependencies=[Depends(require_admin_or_creator)],
)
def update_policy(
policy_id: int,
payload: PolicyUpdate,
db: Session = Depends(get_db),
):
    return policy_service.update_policy(
    db,
    policy_id,
    payload,
    )


@router.delete(
"/admin/{policy_id}",
status_code=204,
dependencies=[Depends(require_admin_or_creator)],
)
def delete_policy(
policy_id: int,
db: Session = Depends(get_db),
):
   return policy_service.delete_policy(
    db,
    policy_id,
    )

