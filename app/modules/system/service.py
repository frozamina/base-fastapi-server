# RBAC 业务服务：登录名/角色编码唯一、最后一名管理员、内置角色
from typing import List, Optional

from app.modules.system import repository as rbac_dao
from app.modules.system.schemas import PermissionOut, RoleBrief, RoleOut, UserOut
from app.shared.service import BaseService


class RbacService(BaseService):
    def to_user_out(self, user) -> UserOut:
        roles = rbac_dao.list_roles_of_user(self.db, user.id)
        perms = rbac_dao.list_perm_codes_of_user(self.db, user.id)
        return UserOut(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            status=user.status,
            roles=[RoleBrief.model_validate(r) for r in roles],
            permissions=perms,
        )

    def to_role_out(self, role) -> RoleOut:
        perms = rbac_dao.list_perms_of_role(self.db, role.id)
        return RoleOut(
            id=role.id,
            role_code=role.role_code,
            role_name=role.role_name,
            description=role.description,
            permissions=[PermissionOut.model_validate(p) for p in perms],
        )

    def list_users(self) -> List[UserOut]:
        return [self.to_user_out(u) for u in rbac_dao.list_users(self.db)]

    def create_user(self, username: str, password: str, real_name: Optional[str],
                    status: int, role_ids: List[int]) -> UserOut:
        if rbac_dao.get_user_by_username(self.db, username):
            raise ValueError("登录名已存在")
        user = rbac_dao.create_user(
            self.db, username, password, real_name, status, role_ids
        )
        self.commit()
        return self.to_user_out(user)

    def update_user(self, user_id: int, real_name=None, password=None,
                    status=None, role_ids=None) -> Optional[UserOut]:
        user = rbac_dao.update_user(
            self.db, user_id, real_name=real_name, password=password,
            status=status, role_ids=role_ids,
        )
        if not user:
            return None
        self.commit()
        return self.to_user_out(user)

    def delete_user(self, user_id: int) -> bool:
        user = rbac_dao.get_user_by_id(self.db, user_id)
        if not user:
            return False
        codes = rbac_dao.list_perm_codes_of_user(self.db, user_id)
        if rbac_dao.user_has_perm(codes, "*"):
            admin_left = 0
            for u in rbac_dao.list_users(self.db):
                if u.id == user_id or u.status != 1:
                    continue
                if rbac_dao.user_has_perm(rbac_dao.list_perm_codes_of_user(self.db, u.id), "*"):
                    admin_left += 1
            if admin_left == 0:
                raise ValueError("不能删除最后一名管理员")
        ok = rbac_dao.delete_user(self.db, user_id)
        if ok:
            self.commit()
        return ok

    def list_roles(self) -> List[RoleOut]:
        return [self.to_role_out(r) for r in rbac_dao.list_roles(self.db)]

    def create_role(self, role_code: str, role_name: str, description: Optional[str],
                    permission_ids: List[int]) -> RoleOut:
        if rbac_dao.get_role_by_code(self.db, role_code):
            raise ValueError("角色编码已存在")
        role = rbac_dao.create_role(
            self.db, role_code, role_name, description, permission_ids
        )
        self.commit()
        return self.to_role_out(role)

    def update_role(self, role_id: int, role_name=None, description=None,
                    permission_ids=None) -> Optional[RoleOut]:
        role = rbac_dao.update_role(
            self.db, role_id, role_name=role_name, description=description,
            permission_ids=permission_ids,
        )
        if not role:
            return None
        self.commit()
        return self.to_role_out(role)

    def delete_role(self, role_id: int) -> bool:
        role = rbac_dao.get_role(self.db, role_id)
        if not role:
            return False
        if role.role_code == "admin":
            raise ValueError("内置管理员角色不能删除")
        if rbac_dao.is_role_bound(self.db, role_id):
            raise ValueError("仍有用户绑定该角色，无法删除")
        ok = rbac_dao.delete_role(self.db, role_id)
        if ok:
            self.commit()
        return ok

    def list_permissions(self):
        return [PermissionOut.model_validate(p) for p in rbac_dao.list_permissions(self.db)]
