# 兼容旧引用：统一响应以 scheme.base.ResponseModel 为准
from typing import Generic, TypeVar

from app.core.responses.base import PageMeta, RequestModel, ResponseModel

T = TypeVar("T")

# 对外继续暴露旧名，避免已有 import 断裂
__all__ = ["ApiResponse", "PageMeta", "RequestModel", "ResponseModel"]


class ApiResponse(ResponseModel[T], Generic[T]):
    """旧名 ApiResponse，字段与 ResponseModel 相同，多了 meta。"""
    pass
