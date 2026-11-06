# 路由依赖：一键注入已绑定 Session 的 Service，接口里不再写 get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database.session import get_db


def service_dep(service_cls):
    """用法：svc: StudentService = Depends(service_dep(StudentService))"""

    def _factory(db: Session = Depends(get_db)):
        return service_cls(db)

    return _factory
