# 手动补种管理员账号。启动应用时也会执行。
from app.core.database.registry import import_models

import_models()

from app.modules.system.seed import seed_rbac

if __name__ == "__main__":
    seed_rbac()
