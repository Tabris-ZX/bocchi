from typing import ClassVar

from nonebot import get_driver
from pydantic import BaseModel, Extra

driver = get_driver()


class ContestConfig(BaseModel, extra=Extra.ignore):
    days: int = 7
    limit: int = 20
    remind_pre: int = 30
    DEFAULT_PARAMS: ClassVar[dict[str, str | int | bool]] = {  # 添加类型注解
        "username": "tabris",
        "api_key": "b8e38d0599c24dcda14f1671e8fd0ff484920686",
        "order_by": "start",
        # "limit": 10,
    }


contest_config = ContestConfig.parse_obj(driver.config.dict())
