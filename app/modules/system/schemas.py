# RBAC 请求 / 响应模型
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.core.responses.base import RequestModel


class RoleBrief(BaseModel):
    id: int
    role_code: str
    role_name: str
    model_config = ConfigDict(from_attributes=True)


class PermissionOut(BaseModel):
    id: int
    perm_code: str
    perm_name: str
    resource: str
    action: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    status: int
    roles: List[RoleBrief] = []
    permissions: List[str] = []
    model_config = ConfigDict(from_attributes=True)


class UserCreate(RequestModel):
    username: str = Field(..., min_length=2, max_length=32)
    password: str = Field(..., min_length=6, max_length=64)
    real_name: Optional[str] = Field(None, max_length=32)
    status: int = Field(1, ge=0, le=1)
    role_ids: List[int] = Field(default_factory=list, description="绑定的角色ID")


class UserUpdate(RequestModel):
    real_name: Optional[str] = Field(None, max_length=32)
    password: Optional[str] = Field(None, min_length=6, max_length=64)
    status: Optional[int] = Field(None, ge=0, le=1)
    role_ids: Optional[List[int]] = None


class RoleCreate(RequestModel):
    role_code: str = Field(..., min_length=2, max_length=32)
    role_name: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(RequestModel):
    role_name: Optional[str] = Field(None, max_length=64)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: Optional[List[int]] = None


class RoleOut(BaseModel):
    id: int
    role_code: str
    role_name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []
    model_config = ConfigDict(from_attributes=True)
