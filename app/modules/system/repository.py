# RBAC 数据访问：用户不直接绑权限，一律经角色
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from app.core.security.token import hash_password
from app.modules.system.models import Permission, Role, RolePermission, User, UserRole


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username, User.is_deleted == 0).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()


def list_roles_of_user(db: Session, user_id: int) -> List[Role]:
    return (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id, Role.is_deleted == 0)
        .all()
    )


def list_perm_codes_of_user(db: Session, user_id: int) -> List[str]:
    """用户权限 = 其所有未删除角色上的权限编码并集。"""
    rows = (
        db.query(Permission.perm_code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id, Role.is_deleted == 0)
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def user_has_perm(codes: Sequence[str], need: str) -> bool:
    """支持 * 超管、resource:* 资源通配。"""
    if "*" in codes or need in codes:
        return True
    if ":" in need:
        resource = need.split(":", 1)[0]
        if f"{resource}:*" in codes:
            return True
    return False


def list_users(db: Session) -> List[User]:
    return db.query(User).filter(User.is_deleted == 0).order_by(User.id).all()


def create_user(db: Session, username: str, password: str, real_name: Optional[str],
                status: int, role_ids: List[int]) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        real_name=real_name,
        status=status,
        is_deleted=0,
    )
    db.add(user)
    db.flush()
    replace_user_roles(db, user.id, role_ids)
    db.flush()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, real_name=None, password=None,
                status=None, role_ids=None) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    if real_name is not None:
        user.real_name = real_name
    if password:
        user.password_hash = hash_password(password)
    if status is not None:
        user.status = status
    if role_ids is not None:
        replace_user_roles(db, user.id, role_ids)
    db.flush()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    user.is_deleted = 1
    db.flush()
    return True


def replace_user_roles(db: Session, user_id: int, role_ids: List[int]) -> None:
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    for rid in dict.fromkeys(role_ids):
        role = db.query(Role).filter(Role.id == rid, Role.is_deleted == 0).first()
        if not role:
            raise ValueError(f"角色不存在或已删除: {rid}")
        db.add(UserRole(user_id=user_id, role_id=rid))


def list_roles(db: Session) -> List[Role]:
    return db.query(Role).filter(Role.is_deleted == 0).order_by(Role.id).all()


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id, Role.is_deleted == 0).first()


def get_role_by_code(db: Session, role_code: str) -> Optional[Role]:
    return db.query(Role).filter(Role.role_code == role_code, Role.is_deleted == 0).first()


def is_role_bound(db: Session, role_id: int) -> bool:
    return db.query(UserRole.id).filter(UserRole.role_id == role_id).first() is not None


def list_perms_of_role(db: Session, role_id: int) -> List[Permission]:
    return (
        db.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role_id)
        .order_by(Permission.resource, Permission.action)
        .all()
    )


def create_role(db: Session, role_code: str, role_name: str, description: Optional[str],
                permission_ids: List[int]) -> Role:
    role = Role(role_code=role_code, role_name=role_name, description=description, is_deleted=0)
    db.add(role)
    db.flush()
    replace_role_perms(db, role.id, permission_ids)
    db.flush()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, role_name=None, description=None,
                permission_ids=None) -> Optional[Role]:
    role = get_role(db, role_id)
    if not role:
        return None
    if role_name is not None:
        role.role_name = role_name
    if description is not None:
        role.description = description
    if permission_ids is not None:
        replace_role_perms(db, role.id, permission_ids)
    db.flush()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    role = get_role(db, role_id)
    if not role:
        return False
    role.is_deleted = 1
    db.flush()
    return True


def replace_role_perms(db: Session, role_id: int, permission_ids: List[int]) -> None:
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for pid in dict.fromkeys(permission_ids):
        perm = db.query(Permission).filter(Permission.id == pid).first()
        if not perm:
            raise ValueError(f"权限不存在: {pid}")
        db.add(RolePermission(role_id=role_id, permission_id=pid))


def list_permissions(db: Session) -> List[Permission]:
    return db.query(Permission).order_by(Permission.resource, Permission.action).all()
