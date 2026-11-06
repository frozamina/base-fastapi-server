# 环境变量和路径。系统里已经设置的变量优先于 .env。
import os
from pathlib import Path
from urllib.parse import quote_plus

# 本文件在 app/core/config/ 下，往上三级是项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _load_dotenv(path: Path) -> None:
    """读 .env。空值跳过，避免盖掉代码里的本地默认。"""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or value == "" or key in os.environ:
            continue
        os.environ[key] = value


_load_dotenv(PROJECT_ROOT / ".env")

# 生产环境请设置 APP_SECRET_KEY，不要用这个开发默认值
SECRET_KEY = os.getenv("APP_SECRET_KEY", "base-fastapi-dev-key")


def database_url() -> str:
    """优先用完整 URL，否则用分项变量拼 MySQL 连接串。"""
    full = os.getenv("APP_DATABASE_URL")
    if full:
        return full
    user = os.getenv("APP_DB_USER", "root")
    password = os.getenv("APP_DB_PASSWORD", "123456")
    host = os.getenv("APP_DB_HOST", "localhost")
    port = os.getenv("APP_DB_PORT", "3306")
    name = os.getenv("APP_DB_NAME", "base_app")
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{name}?charset=utf8mb4"
    )
