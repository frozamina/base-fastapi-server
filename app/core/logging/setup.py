# 应用自己的日志名。请求访问日志仍由 uvicorn 输出。
import logging


def setup_logging() -> None:
    logging.getLogger("app").setLevel(logging.INFO)
