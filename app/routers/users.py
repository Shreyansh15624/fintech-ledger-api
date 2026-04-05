from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter(
    prefix="/api/v1/users",
    tags=["User Management"],
)

# ADMIN: View all Users
@router.get("/", response_model=List[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker({"Admin"}))
):
    users = db.query(models.User).filter(models.User.is_active == True).all()
    return users

# ADMIN: View all Soft Deleted Users
@router.get("/soft_deleted", response_model=List[schemas.UserResponse])
def get_all_soft_deleted_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker({"Admin"}))
):
    users = db.query(models.User).filter(models.User.is_active == False).all()
    return users

# ADMIN: Updates the User Roles
@router.put("/{user_id}/role")
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

# ADMIN: Soft Delete Users (Deactivation)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_users: models.User = Depends(RoleChecker({"Admin"}))
):
    user_query = db.query(models.User).filter(models.User.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )
    
    # The Soft Delete: We don't delete the row, we just turn off the access
    user_query.update({"is_active": False}, synchronize_session=False)
    db.commit()

    return None