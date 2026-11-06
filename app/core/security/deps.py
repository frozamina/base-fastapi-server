# FastAPI 依赖：解析当前用户、校验角色权限
from dataclasses import dataclass, field
from typing import List, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions.errors import AuthError, ForbiddenError
from app.core.security.token import parse_token
from app.modules.system import repository as rbac_dao
from app.core.database.session import get_db
from app.modules.system.schemas import RoleBrief

# auto_error=False：方便登录接口不带 Token；业务接口自行判断
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """请求上下文中的登录用户（含角色与权限编码）。"""

    id: int
    username: str
    real_name: Optional[str]
    status: int
    roles: List[RoleBrief] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """从 Authorization: Bearer 解析用户；失败返回 401。"""
    if not creds or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise AuthError("未登录或令牌缺失")
    payload = parse_token(creds.credentials)
    if not payload:
        raise AuthError("JWT 无效或已过期")
    user = rbac_dao.get_user_by_id(db, int(payload["uid"]))
    if not user:
        raise AuthError("用户不存在或已删除")
    if user.status != 1:
        raise ForbiddenError("账号已停用")
    roles = rbac_dao.list_roles_of_user(db, user.id)
    perms = rbac_dao.list_perm_codes_of_user(db, user.id)
    return CurrentUser(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        status=user.status,
        roles=[RoleBrief.model_validate(r) for r in roles],
        permissions=perms,
    )


def module_guard(resource: str, read_only: bool = False):
    """按 HTTP 方法映射为 resource:read/write/delete，挂到整个路由器上。"""

    def _dep(request: Request, user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        method = request.method.upper()
        if read_only or method in ("GET", "HEAD", "OPTIONS"):
            action = "read"
        elif method == "DELETE":
            action = "delete"
        else:
            action = "write"
        need = f"{resource}:{action}"
        if not rbac_dao.user_has_perm(user.permissions, need):
            raise ForbiddenError(f"没有权限: {need}")
        return user

    return _dep
