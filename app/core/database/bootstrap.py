# 启动时拆掉物理外键。新表只保留逻辑外键字段和普通索引。
from sqlalchemy import inspect, text

from app.core.database.session import engine


def drop_physical_foreign_keys() -> int:
    """拆除当前库中全部 FOREIGN KEY，避免物理锁死导致无法软删。"""
    inspector = inspect(engine)
    dropped = 0
    with engine.begin() as conn:
        for table_name in inspector.get_table_names():
            for fk in inspector.get_foreign_keys(table_name):
                name = fk.get("name")
                if not name:
                    continue
                conn.execute(text(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{name}`"))
                dropped += 1
    return dropped


def apply() -> None:
    drop_physical_foreign_keys()


apply()
