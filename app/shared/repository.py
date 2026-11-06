# DAO 基类：只负责落库，不写业务规则
from typing import Any, List, Optional, Type

from sqlalchemy.orm import Session


class BaseDAO:
    """通用数据访问。子类指定 model，必要时覆盖 pk / 软删取值。"""

    model: Type[Any] = None
    pk: str = "id"
    # 成绩/班级历史用过 Boolean，统一按“非 0 即删”不在这里强转
    active_value: Any = 0
    deleted_value: Any = 1

    @classmethod
    def _pk_col(cls):
        return getattr(cls.model, cls.pk)

    @classmethod
    def query_active(cls, db: Session):
        """未删除记录查询。"""
        return db.query(cls.model).filter(cls.model.is_deleted == cls.active_value)

    @classmethod
    def get_by_id(cls, db: Session, ident: Any):
        return cls.query_active(db).filter(cls._pk_col() == ident).first()

    @classmethod
    def list_all(cls, db: Session, skip: int = 0, limit: int = 100) -> List:
        return (
            cls.query_active(db)
            .order_by(cls._pk_col())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def add(cls, db: Session, obj):
        """加入会话并 flush，不提交。提交由 get_db 在请求结束时完成。"""
        db.add(obj)
        db.flush()
        db.refresh(obj)
        return obj

    @classmethod
    def save(cls, db: Session, obj):
        """把已跟踪对象的改动 flush 到连接，不提交。"""
        db.flush()
        db.refresh(obj)
        return obj

    @classmethod
    def soft_delete_obj(cls, db: Session, obj) -> bool:
        if obj is None:
            return False
        obj.is_deleted = cls.deleted_value
        db.flush()
        return True

    @classmethod
    def soft_delete(cls, db: Session, ident: Any) -> bool:
        obj = cls.get_by_id(db, ident)
        return cls.soft_delete_obj(db, obj)
