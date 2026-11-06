# 登录与当前用户信息，不经过角色鉴权（登录前还没有 Token）
from fastapi import APIRouter, Depends

from app.core.security.deps import CurrentUser, get_current_user
from app.modules.auth.schemas import LoginRequest, LoginResponse
from app.modules.system.schemas import UserOut
from app.modules.auth.service import AuthService
from app.shared.deps import service_dep

router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="账号登录")
def login(body: LoginRequest, svc: AuthService = Depends(service_dep(AuthService))):
    return svc.login(body.username, body.password)


@router.get("/me", response_model=UserOut, summary="当前登录用户")
def me(user: CurrentUser = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        status=user.status,
        roles=user.roles,
        permissions=user.permissions,
    )
