from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter(
    prefix="/api/v1/users",
    tags=["User Management"],
)

# ADMIN: Updates the User Roles
@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),

    # Privilege is strictly locked to Admin, sothat only they may promote / demote
    current_user: models.User = Depends(RoleChecker({"Admin"}))
):
    valid_roles = {"Admin", "Analyst", "Viewer"}
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Role! Must be one of {valid_roles}",
        )
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_query.update({"role": new_role}, synchronize_session=False)
    db.commit()

    return {"message": f"User: {user.username} role updated to {new_role}"}