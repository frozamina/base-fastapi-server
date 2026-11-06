# 导入全部 ORM，create_all 才能看到每张表
def import_models() -> None:
    from app.modules.system import models as system_models  # noqa: F401

    from sqlalchemy.orm import configure_mappers

    configure_mappers()
