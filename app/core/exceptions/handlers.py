# 全局异常处理：所有失败都走 {code, message, data, meta}
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions.errors import AppError
from app.core.responses.base import ResponseModel

logger = logging.getLogger("app")


def _body(code: int, message: str, data: Any = None) -> dict:
    """统一信封；附带 detail 给旧前端读。"""
    payload = ResponseModel(code=code, message=message, data=data, meta=None).model_dump()
    payload["detail"] = message
    return payload


def _json(code: int, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(status_code=code, content=_body(code, message, data))


def _http_message(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "；".join(str(x) for x in detail)
    return str(detail) if detail is not None else "请求失败"


def register_exception_handlers(app: FastAPI) -> None:
    """在 FastAPI 上挂统一异常处理。"""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return _json(exc.code, exc.message, exc.data)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        parts = []
        for err in exc.errors():
            loc = ".".join(str(x) for x in err.get("loc", []) if x not in ("body", "query", "path"))
            msg = err.get("msg", "参数不合法")
            parts.append(f"{loc}: {msg}" if loc else msg)
        return _json(422, "；".join(parts) or "参数校验失败")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        return _json(exc.status_code, _http_message(exc.detail))

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_handler(_: Request, exc: StarletteHTTPException):
        return _json(exc.status_code, _http_message(exc.detail))

    @app.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError):
        msg = str(exc) or "业务校验失败"
        code = 400 if ("重复" in msg or "已录入" in msg) else 422
        return _json(code, msg)

    @app.exception_handler(PermissionError)
    async def permission_error_handler(_: Request, exc: PermissionError):
        msg = str(exc) or "没有权限"
        code = 403 if ("停用" in msg or "权限" in msg) else 401
        return _json(code, msg)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError):
        logger.warning("唯一约束或数据冲突: %s", exc)
        return _json(400, "数据冲突，可能违反唯一约束")

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception):
        logger.exception("未处理异常")
        return _json(500, "服务器内部错误")
