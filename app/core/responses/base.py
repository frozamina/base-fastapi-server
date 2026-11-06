# 请求 / 响应模型基类
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class RequestModel(BaseModel):
    """请求体基类。具体接口在子类里声明业务字段。"""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class PageMeta(BaseModel):
    """分页等附加信息，放在统一响应的 meta 里。"""

    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应：
    { "code": 200, "message": "success", "data": ..., "meta": ... }
    """

    code: int = Field(200, description="业务状态码")
    message: str = Field("success", description="提示信息")
    data: Optional[T] = Field(None, description="业务数据")
    meta: Optional[Any] = Field(None, description="分页或其他附加信息")
