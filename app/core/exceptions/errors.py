# 业务异常：路由里抛这些，由全局处理器转成统一响应
from typing import Any, Optional


class AppError(Exception):
    """可预期的业务失败。code 同时作为 HTTP 状态码。"""

    def __init__(self, message: str, code: int = 400, data: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


class AuthError(AppError):
    """未登录或令牌无效。"""

    def __init__(self, message: str = "未登录或令牌缺失", data: Any = None):
        super().__init__(message, code=401, data=data)


class ForbiddenError(AppError):
    """已登录但无权限。"""

    def __init__(self, message: str = "没有权限", data: Any = None):
        super().__init__(message, code=403, data=data)


class NotFoundError(AppError):
    """资源不存在。"""

    def __init__(self, message: str = "资源不存在", data: Any = None):
        super().__init__(message, code=404, data=data)


class BizError(AppError):
    """校验/规则失败，默认 422。"""

    def __init__(self, message: str, code: int = 422, data: Any = None):
        super().__init__(message, code=code, data=data)
