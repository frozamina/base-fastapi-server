# 首次启动写入权限点、管理员角色和演示账号（幂等）
from sqlalchemy.orm import Session

from app.core.database.session import SessionLocal
from app.core.security.token import hash_password
from app.modules.system.models import Permission, Role, RolePermission, User, UserRole

# 权限点：资源:动作。* 表示超级管理员。业务模块的权限在新项目里再加。
PERMISSIONS = [
    ("*", "超级管理员", "*", "*"),
    ("rbac:read", "查看用户与角色", "rbac", "read"),
    ("rbac:write", "维护用户与角色", "rbac", "write"),
    ("rbac:delete", "删除用户与角色", "rbac", "delete"),
]

ROLES = {
    "admin": ("系统管理员", "拥有全部权限", ["*"]),
}

# 演示账号只用于本机。生产环境请立刻改掉密码。
USERS = [
    ("admin", "admin123", "系统管理员", "admin"),
]


def _ensure_permissions(db: Session) -> dict:
    mapping = {}
    for code, name, resource, action in PERMISSIONS:
        row = db.query(Permission).filter(Permission.perm_code == code).first()
        if not row:
            row = Permission(
                perm_code=code, perm_name=name, resource=resource, action=action,
                description=name,
            )
            db.add(row)
            db.flush()
        mapping[code] = row
    return mapping


def _ensure_roles(db: Session, perms: dict) -> dict:
    mapping = {}
    for code, (name, desc, perm_codes) in ROLES.items():
        role = db.query(Role).filter(Role.role_code == code, Role.is_deleted == 0).first()
        if not role:
            role = Role(role_code=code, role_name=name, description=desc, is_deleted=0)
            db.add(role)
            db.flush()
        mapping[code] = role
        db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
        for pc in perm_codes:
            perm = perms.get(pc)
            if perm:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    return mapping


def _ensure_users(db: Session, roles: dict) -> None:
    for username, password, real_name, role_code in USERS:
        user = db.query(User).filter(User.username == username, User.is_deleted == 0).first()
        if not user:
            user = User(
                username=username,
                password_hash=hash_password(password),
                real_name=real_name,
                status=1,
                is_deleted=0,
            )
            db.add(user)
            db.flush()
        role = roles.get(role_code)
        if not role:
            continue
        exists = (
            db.query(UserRole)
            .filter(UserRole.user_id == user.id, UserRole.role_id == role.id)
            .first()
        )
        if not exists:
            db.add(UserRole(user_id=user.id, role_id=role.id))


def seed_rbac() -> None:
    """创建表后写入内置 RBAC 数据，可重复执行。"""
    db = SessionLocal()
    try:
        perms = _ensure_permissions(db)
        roles = _ensure_roles(db, perms)
        _ensure_users(db, roles)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
