# 表模型基类：统一审计字段。id 类型因业务不同，由子类声明或使用 IntIdTableModel
from sqlalchemy import BigInteger, Column, DateTime, Integer, text
from sqlalchemy.orm import declared_attr, synonym
from sqlalchemy.sql import func

from app.core.database.session import Base


class AuditTableModel(Base):
    """
    表模型公共字段：is_deleted / created_at / updated_at。
    旧表列名不一致时，子类设置 __created_at_name__ / __updated_at_name__。
    """

    __abstract__ = True
    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"

    is_deleted = Column(
        Integer, nullable=False, server_default=text("0"),
        comment="逻辑删除：0 未删除，1 已删除",
    )

    @declared_attr
    def created_at(cls):
        return Column(
            cls.__created_at_name__, DateTime, nullable=True,
            server_default=func.now(), comment="创建时间",
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            cls.__updated_at_name__, DateTime, nullable=True,
            server_default=func.now(), onupdate=func.now(), comment="更新时间",
        )

    @declared_attr
    def create_time(cls):
        """兼容旧代码里的 create_time。"""
        return synonym("created_at")

    @declared_attr
    def update_time(cls):
        """兼容旧代码里的 update_time。"""
        return synonym("updated_at")


class IntIdTableModel(AuditTableModel):
    """自增整型主键表。业务主键不是自增数字时不要用这个。"""

    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
