# 登录业务：校验账号密码，组 Token 所需数据
from app.core.security.token import TOKEN_EXPIRE_SECONDS, create_token, verify_password
from app.modules.system import repository as rbac_dao
from app.modules.auth.schemas import LoginResponse
from app.modules.system.schemas import RoleBrief
from app.shared.service import BaseService


class AuthService(BaseService):
    def login(self, username: str, password: str) -> LoginResponse:
        user = rbac_dao.get_user_by_username(self.db, username)
        if not user or not verify_password(password, user.password_hash):
            raise PermissionError("用户名或密码错误")
        if user.status != 1:
            raise PermissionError("账号已停用")
        roles = rbac_dao.list_roles_of_user(self.db, user.id)
        perms = rbac_dao.list_perm_codes_of_user(self.db, user.id)
        return LoginResponse(
            token=create_token(user.id, user.username),
            token_type="Bearer",
            expires_in=TOKEN_EXPIRE_SECONDS,
            user_id=user.id,
            username=user.username,
            real_name=user.real_name,
            roles=[RoleBrief.model_validate(r) for r in roles],
            permissions=perms,
        )
