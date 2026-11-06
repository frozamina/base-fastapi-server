# Controller 基类：统一包装 HTTP 响应，不写 SQL
from typing import Any, Optional

from app.core.exceptions.errors import AppError, NotFoundError
from app.core.responses.base import PageMeta, ResponseModel


class BaseController:
    """接口层公共方法。具体路由函数调用 ok / fail / not_found。"""

    @staticmethod
    def ok(data: Any = None, message: str = "success", meta: Any = None, code: int = 200) -> dict:
        """成功响应：{code, message, data, meta}。"""
        return ResponseModel(code=code, message=message, data=data, meta=meta).model_dump()

    @staticmethod
    def page(items, total: int, skip: int = None, limit: int = None,
             page: int = None, page_size: int = None, message: str = "success") -> dict:
        """列表分页，把 total 等放进 meta，items 放进 data。"""
        meta = PageMeta(
            total=total, skip=skip, limit=limit, page=page, page_size=page_size,
        ).model_dump(exclude_none=True)
        return BaseController.ok(data=items, message=message, meta=meta)

    @staticmethod
    def fail(message: str, code: int = 400, data: Any = None) -> None:
        """失败抛业务异常，由全局处理器包装。"""
        raise AppError(message, code=code, data=data)

    @staticmethod
    def not_found(message: str = "资源不存在") -> None:
        raise NotFoundError(message)
