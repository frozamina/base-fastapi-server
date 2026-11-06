# Service 基类：编排业务并提交事务，不直接拼 SQL
from typing import Any, Type

from sqlalchemy.orm import Session

from app.shared.repository import BaseDAO


class BaseService:
    """子类指定 dao。实例绑定当前请求的 Session，写操作结束时自行 commit。"""

    dao: Type[BaseDAO] = None

    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        """所有 DAO 干完后由 Service 一次性提交。"""
        self.db.commit()

    def get_by_id(self, ident: Any):
        return self.dao.get_by_id(self.db, ident)

    def list_all(self, skip: int = 0, limit: int = 100):
        return self.dao.list_all(self.db, skip=skip, limit=limit)

    def remove(self, ident: Any) -> bool:
        ok = self.dao.soft_delete(self.db, ident)
        if ok:
            self.commit()
        return ok
