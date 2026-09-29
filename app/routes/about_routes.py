from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import require_admin_or_creator

from app.services import about_service

from app.schemas.about import (
    # About Page
    AboutPageCreate,
    AboutPageUpdate,
    AboutPageOut,
    # Leadership
    AboutLeadershipCreate,
    AboutLeadershipUpdate,
    AboutLeadershipOut,
    AboutLeadershipPublicOut,
    # Team
    AboutTeamMemberCreate,
    AboutTeamMemberUpdate,
    AboutTeamMemberOut,
    AboutTeamMemberPublicOut,
    # Milestones
    AboutMilestoneCreate,
    AboutMilestoneUpdate,
    AboutMilestoneOut,
    AboutMilestonePublicOut,
    # Values
    AboutValueCreate,
    AboutValueUpdate,
    AboutValueOut,
    AboutValuePublicOut,
    # Complete public About response
    AboutPublicPageOut,
)

router = APIRouter(
    prefix="/about",
    tags=["About"],
)


# ============================================================
# PUBLIC - COMPLETE ABOUT PAGE
# ============================================================


@router.get(
    "",
    response_model=AboutPublicPageOut,
    status_code=status.HTTP_200_OK,
)
def get_public_about(
    db: Session = Depends(get_db),
):
    """
    Get the complete public About page.

    Includes:
    - Company information
    - Leadership
    - Team members
    - Milestones
    - Company values
    """
    return about_service.get_public_about_page(db)


# ============================================================
# PUBLIC - LEADERSHIP
# ============================================================


@router.get(
    "/leadership",
    response_model=list[AboutLeadershipPublicOut],
    status_code=status.HTTP_200_OK,
)
def get_public_leadership(
    db: Session = Depends(get_db),
):
    """
    Get all active leadership profiles.
    """
    return about_service.get_public_leadership(db)


@router.get(
    "/leadership/{slug}",
    response_model=AboutLeadershipPublicOut,
    status_code=status.HTTP_200_OK,
)
def get_public_leadership_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get one active leadership profile by slug.

    Used for:
        /about/leadership/{slug}
    """
    return about_service.get_public_leadership_by_slug(
        db,
        slug,
    )


# ============================================================
# PUBLIC - TEAM MEMBERS
# ============================================================


@router.get(
    "/team",
    response_model=list[AboutTeamMemberPublicOut],
    status_code=status.HTTP_200_OK,
)
def get_public_team_members(
    db: Session = Depends(get_db),
):
    """
    Get all active team members.
    """
    return about_service.get_public_team_members(db)


@router.get(
    "/team/{slug}",
    response_model=AboutTeamMemberPublicOut,
    status_code=status.HTTP_200_OK,
)
def get_public_team_member_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get one publicly visible team member by slug.

    The service only returns the profile when:
    - is_active = True
    - show_public_profile = True
    """
    return about_service.get_public_team_member_by_slug(
        db,
        slug,
    )


# ============================================================
# ADMIN - ABOUT PAGE
# ============================================================


@router.get(
    "/admin",
    response_model=AboutPageOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_about_page_admin(
    db: Session = Depends(get_db),
):
    """
    Get the About page for admin/creator management.
    """
    return about_service.get_about_page_admin(db)


@router.post(
    "/admin",
    response_model=AboutPageOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_about_page(
    payload: AboutPageCreate,
    db: Session = Depends(get_db),
):
    """
    Create the About page.

    Only one AboutPage record is allowed.
    """
    return about_service.create_about_page(
        db,
        payload,
    )


@router.put(
    "/admin",
    response_model=AboutPageOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_about_page(
    payload: AboutPageUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the existing About page.
    """
    return about_service.update_about_page(
        db,
        payload,
    )


# ============================================================
# ADMIN - LEADERSHIP
# ============================================================


@router.get(
    "/admin/leadership",
    response_model=list[AboutLeadershipOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_all_leadership_admin(
    db: Session = Depends(get_db),
):
    """
    Get all leadership records for admin/creator.
    Includes active and inactive records.
    """
    return about_service.get_all_leadership_admin(db)


@router.post(
    "/admin/leadership",
    response_model=AboutLeadershipOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_leadership(
    payload: AboutLeadershipCreate,
    db: Session = Depends(get_db),
):
    """
    Create a leadership profile.

    Slug is generated automatically by the service.
    """
    return about_service.create_leadership(
        db,
        payload,
    )


@router.put(
    "/admin/leadership/{item_id}",
    response_model=AboutLeadershipOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_leadership(
    item_id: int,
    payload: AboutLeadershipUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a leadership profile by ID.
    """
    return about_service.update_leadership(
        db,
        item_id,
        payload,
    )


@router.delete(
    "/admin/leadership/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_leadership(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a leadership profile by ID.
    """
    about_service.delete_leadership(
        db,
        item_id,
    )

    return None


# ============================================================
# ADMIN - TEAM MEMBERS
# ============================================================


@router.get(
    "/admin/team",
    response_model=list[AboutTeamMemberOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_all_team_members_admin(
    db: Session = Depends(get_db),
):
    """
    Get all team members for admin/creator.

    Includes:
    - Active members
    - Inactive members
    - Profiles hidden from public
    """
    return about_service.get_all_team_members_admin(db)


@router.post(
    "/admin/team",
    response_model=AboutTeamMemberOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_team_member(
    payload: AboutTeamMemberCreate,
    db: Session = Depends(get_db),
):
    """
    Create a team member.

    Slug is generated automatically by the service.
    """
    return about_service.create_team_member(
        db,
        payload,
    )


@router.put(
    "/admin/team/{item_id}",
    response_model=AboutTeamMemberOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_team_member(
    item_id: int,
    payload: AboutTeamMemberUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a team member by ID.
    """
    return about_service.update_team_member(
        db,
        item_id,
        payload,
    )


@router.delete(
    "/admin/team/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_team_member(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a team member by ID.
    """
    about_service.delete_team_member(
        db,
        item_id,
    )

    return None


# ============================================================
# ADMIN - MILESTONES
# ============================================================


@router.get(
    "/admin/milestones",
    response_model=list[AboutMilestoneOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_all_milestones_admin(
    db: Session = Depends(get_db),
):
    """
    Get all milestones for admin/creator.
    """
    return about_service.get_all_milestones_admin(db)


@router.post(
    "/admin/milestones",
    response_model=AboutMilestoneOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_milestone(
    payload: AboutMilestoneCreate,
    db: Session = Depends(get_db),
):
    """
    Create a company milestone.
    """
    return about_service.create_milestone(
        db,
        payload,
    )


@router.put(
    "/admin/milestones/{item_id}",
    response_model=AboutMilestoneOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_milestone(
    item_id: int,
    payload: AboutMilestoneUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a company milestone by ID.
    """
    return about_service.update_milestone(
        db,
        item_id,
        payload,
    )


@router.delete(
    "/admin/milestones/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_milestone(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a company milestone by ID.
    """
    about_service.delete_milestone(
        db,
        item_id,
    )

    return None


# ============================================================
# ADMIN - VALUES
# ============================================================


@router.get(
    "/admin/values",
    response_model=list[AboutValueOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def get_all_values_admin(
    db: Session = Depends(get_db),
):
    """
    Get all company values for admin/creator.
    """
    return about_service.get_all_values_admin(db)


@router.post(
    "/admin/values",
    response_model=AboutValueOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_creator)],
)
def create_value(
    payload: AboutValueCreate,
    db: Session = Depends(get_db),
):
    """
    Create a company value.
    """
    return about_service.create_value(
        db,
        payload,
    )


@router.put(
    "/admin/values/{item_id}",
    response_model=AboutValueOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_creator)],
)
def update_value(
    item_id: int,
    payload: AboutValueUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a company value by ID.
    """
    return about_service.update_value(
        db,
        item_id,
        payload,
    )


@router.delete(
    "/admin/values/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_creator)],
)
def delete_value(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a company value by ID.
    """
    about_service.delete_value(
        db,
        item_id,
    )

    return None
