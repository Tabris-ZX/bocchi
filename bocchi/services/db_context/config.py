from collections.abc import Callable

from pydantic import BaseModel

# 数据库操作超时设置（秒）
DB_TIMEOUT_SECONDS = 8.0

# 性能监控阈值（秒）
SLOW_QUERY_THRESHOLD = 0.5

LOG_COMMAND = "DbContext"


POSTGRESQL_CONFIG = {
    "max_size": 20,  # 最大连接数（2核4G：适中并发，避免上下文切换开销）
    "min_size": 2,  # 最小保持的连接数（减小内存占用）
}


MYSQL_CONFIG = {
    "max_connections": 20,  # 最大连接数
    "connect_timeout": 30,  # 连接超时（可选）
}

SQLITE_CONFIG = {
    "journal_mode": "WAL",  # 提高并发写入性能
    "timeout": 30,  # 锁等待超时（可选）
}


class DbModel(BaseModel):
    script_method: list[tuple[str, Callable]] = []
    models: list[str] = []


db_model = DbModel()


prompt = """
**********************************************************************
🌟 **************************** 配置为空 ************************* 🌟
🚀 请打开 WebUi 进行基础配置 🚀
🌐 配置地址：http://{host}:{port}/#/configure 🌐
***********************************************************************
***********************************************************************
"""
