# 登录请求和令牌响应。角色摘要仍放在系统模块。
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.responses.base import RequestModel
from app.modules.system.schemas import RoleBrief


class LoginRequest(RequestModel):
    username: str = Field(..., min_length=1, max_length=32, description="登录名")
    password: str = Field(..., min_length=1, max_length=64, description="密码")


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    expires_in: int = Field(12 * 3600, description="JWT 有效秒数")
    user_id: int
    username: str
    real_name: Optional[str] = None
    roles: List[RoleBrief]
    permissions: List[str]
