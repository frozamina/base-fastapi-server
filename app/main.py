# 应用入口：建表、注册路由
from fastapi import FastAPI

from app.core.database.registry import import_models
from app.core.database.session import Base, engine

import_models()
import app.core.database.bootstrap  # noqa: F401  启动时拆掉物理外键

from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging.setup import setup_logging
from app.core.middleware.cors import install_cors
from app.modules.auth.router import router as auth_router
from app.modules.system.router import router as system_router
from app.modules.system.seed import seed_rbac
from app.shared.constants.app import APP_TITLE, APP_VERSION

Base.metadata.create_all(bind=engine)
seed_rbac()
setup_logging()

app = FastAPI(title=APP_TITLE, version=APP_VERSION)
register_exception_handlers(app)
install_cors(app)

app.include_router(auth_router, prefix="/api/auth", tags=["登录认证"])
app.include_router(system_router, prefix="/api/rbac", tags=["角色权限管理"])


@app.get("/")
async def root():
    return {"message": "基项目已启动。请访问 /docs 查看 API 文档。"}


if __name__ == "__main__":
    # 在项目根目录执行：python -m app.main
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
