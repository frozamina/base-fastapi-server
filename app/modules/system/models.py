# RBAC 五张表：用户 / 角色 / 权限 + 两张关系表（逻辑外键，不建物理 CONSTRAINT）
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.core.database.session import Base
from app.core.database.tables import IntIdTableModel


class User(IntIdTableModel):
    """系统用户。权限不直接挂在用户上，只通过角色获得。"""

    __tablename__ = "sys_user"
    __created_at_name__ = "create_time"
    __updated_at_name__ = "update_time"
    username = Column(String(32), unique=True, nullable=False, index=True, comment="登录名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(32), nullable=True, comment="显示姓名")
    status = Column(Integer, nullable=False, server_default=text("1"), comment="1启用 0停用")
    # is_deleted / created_at / updated_at 来自 IntIdTableModel

    user_roles = relationship(
        "UserRole",
        primaryjoin="User.id==UserRole.user_id",
        foreign_keys="[UserRole.user_id]",
        viewonly=True,
    )


class Role(IntIdTableModel):
    """角色：权限的集合，是用户与权限之间的中间层。"""

    __tablename__ = "sys_role"
    __created_at_name__ = "create_time"
    __updated_at_name__ = "update_time"

    role_code = Column(String(32), unique=True, nullable=False, index=True, comment="角色编码，如 admin")
    role_name = Column(String(64), nullable=False, comment="角色名称")
    description = Column(String(255), nullable=True, comment="说明")


class Permission(Base):
    """权限点：resource:action，例如 student:write。"""

    __tablename__ = "sys_permission"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="权限主键")
    perm_code = Column(String(64), unique=True, nullable=False, index=True, comment="权限编码")
    perm_name = Column(String(64), nullable=False, comment="权限名称")
    resource = Column(String(32), nullable=False, index=True, comment="资源，如 student")
    action = Column(String(16), nullable=False, comment="动作 read/write/delete/*")
    description = Column(String(255), nullable=True, comment="说明")


class UserRole(Base):
    """用户-角色关系。user_id / role_id 为逻辑外键。"""

    __tablename__ = "sys_user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uk_user_role"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True, comment="逻辑外键：sys_user.id")
    role_id = Column(BigInteger, nullable=False, index=True, comment="逻辑外键：sys_role.id")
    create_time = Column(DateTime, nullable=False, server_default=func.now())


class RolePermission(Base):
    """角色-权限关系。role_id / permission_id 为逻辑外键。"""

    __tablename__ = "sys_role_permission"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uk_role_perm"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, nullable=False, index=True, comment="逻辑外键：sys_role.id")
    permission_id = Column(BigInteger, nullable=False, index=True, comment="逻辑外键：sys_permission.id")
    create_time = Column(DateTime, nullable=False, server_default=func.now())
