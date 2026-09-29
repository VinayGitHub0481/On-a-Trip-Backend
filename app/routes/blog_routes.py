from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.blog import BlogCreate, BlogUpdate, BlogOut
from app.services import blog_service
from app.core.deps import require_admin_or_creator
from app.models.user import User

router = APIRouter(prefix="/blogs", tags=["Blog"])


@router.get("", response_model=list[dict])
def list_published_blogs(db: Session = Depends(get_db)):
    return blog_service.get_published_blogs(db)


@router.get("/slug/{slug}", response_model=dict)
def get_blog_by_slug(slug: str, db: Session = Depends(get_db)):
    return blog_service.get_blog_by_slug(db, slug)


@router.get(
    "/admin/all",
    response_model=list[BlogOut],
    dependencies=[Depends(require_admin_or_creator)],
)
def list_all_blogs(db: Session = Depends(get_db)):
    return blog_service.get_all_blogs_admin(db)


@router.post("/admin", response_model=BlogOut)
def create_blog(
    payload: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_creator),
):
    return blog_service.create_blog(db, payload, current_user.id)


@router.put(
    "/admin/{blog_id}",
    response_model=BlogOut,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_blog(blog_id: int, payload: BlogUpdate, db: Session = Depends(get_db)):
    return blog_service.update_blog(db, blog_id, payload)


@router.delete(
    "/admin/{blog_id}",
    status_code=204,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog_service.delete_blog(db, blog_id)
