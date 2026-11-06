# 用户 / 角色 / 权限管理（权限来自角色，不直接改用户权限）
from typing import List

from fastapi import APIRouter, Depends

from app.core.security.deps import module_guard
from app.core.exceptions.errors import NotFoundError
from app.modules.system.schemas import (
    PermissionOut, RoleCreate, RoleOut, RoleUpdate,
    UserCreate, UserOut, UserUpdate,
)
from app.shared.deps import service_dep
from app.modules.system.service import RbacService

router = APIRouter(dependencies=[Depends(module_guard("rbac"))])


@router.get("/users", response_model=List[UserOut], summary="用户列表")
def list_users(svc: RbacService = Depends(service_dep(RbacService))):
    return svc.list_users()


@router.post("/users", response_model=UserOut, summary="新增用户并绑定角色")
def create_user(body: UserCreate, svc: RbacService = Depends(service_dep(RbacService))):
    return svc.create_user(
        body.username, body.password, body.real_name, body.status, body.role_ids
    )


@router.put("/users/{user_id}", response_model=UserOut, summary="修改用户或重绑角色")
def update_user(user_id: int, body: UserUpdate, svc: RbacService = Depends(service_dep(RbacService))):
    user = svc.update_user(
        user_id,
        real_name=body.real_name,
        password=body.password,
        status=body.status,
        role_ids=body.role_ids,
    )
    if not user:
        raise NotFoundError("用户不存在")
    return user


@router.delete("/users/{user_id}", summary="逻辑删除用户")
def delete_user(user_id: int, svc: RbacService = Depends(service_dep(RbacService))):
    if not svc.delete_user(user_id):
        raise NotFoundError("用户不存在")
    return {"msg": "删除成功"}


@router.get("/roles", response_model=List[RoleOut], summary="角色列表")
def list_roles(svc: RbacService = Depends(service_dep(RbacService))):
    return svc.list_roles()


@router.post("/roles", response_model=RoleOut, summary="新增角色并配置权限")
def create_role(body: RoleCreate, svc: RbacService = Depends(service_dep(RbacService))):
    return svc.create_role(
        body.role_code, body.role_name, body.description, body.permission_ids
    )


@router.put("/roles/{role_id}", response_model=RoleOut, summary="修改角色或重配权限")
def update_role(role_id: int, body: RoleUpdate, svc: RbacService = Depends(service_dep(RbacService))):
    role = svc.update_role(
        role_id,
        role_name=body.role_name,
        description=body.description,
        permission_ids=body.permission_ids,
    )
    if not role:
        raise NotFoundError("角色不存在")
    return role


@router.delete("/roles/{role_id}", summary="逻辑删除角色")
def delete_role(role_id: int, svc: RbacService = Depends(service_dep(RbacService))):
    if not svc.delete_role(role_id):
        raise NotFoundError("角色不存在")
    return {"msg": "删除成功"}


@router.get("/permissions", response_model=List[PermissionOut], summary="权限点列表")
def list_permissions(svc: RbacService = Depends(service_dep(RbacService))):
    return svc.list_permissions()
