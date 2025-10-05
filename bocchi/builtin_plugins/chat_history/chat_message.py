from nonebot import on_message
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import UniMsg
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_uninfo import Uninfo

from bocchi.configs.config import Config
from bocchi.configs.utils import PluginExtraData, RegisterConfig
from bocchi.models.chat_history import ChatHistory
from bocchi.services.log import logger
from bocchi.utils.enum import PluginType
from bocchi.utils.utils import get_entity_ids
from bocchi.services.db_context.utils import with_db_timeout

__plugin_meta__ = PluginMetadata(
    name="消息存储",
    description="消息存储，被动存储群消息",
    usage="",
    extra=PluginExtraData(
        author="HibiKier",
        version="0.1",
        plugin_type=PluginType.HIDDEN,
        configs=[
            RegisterConfig(
                module="chat_history",
                key="FLAG",
                value=True,
                help="是否开启消息自从存储",
                default_value=True,
                type=bool,
            )
        ],
    ).to_dict(),
)


def rule(message: UniMsg) -> bool:
    return bool(Config.get_config("chat_history", "FLAG") and message)


chat_history = on_message(rule=rule, priority=1, block=False)

TEMP_LIST = []


@chat_history.handle()
async def _(message: UniMsg, session: Uninfo):
    entity = get_entity_ids(session)
    TEMP_LIST.append(
        ChatHistory(
            user_id=entity.user_id,
            group_id=entity.group_id,
            text=str(message),
            plain_text=message.extract_plain_text(),
            bot_id=session.self_id,
            platform=session.platform,
        )
    )


@scheduler.scheduled_job(
    "interval",
    seconds=10,
)
async def _():
    try:
        message_list = TEMP_LIST.copy()
        TEMP_LIST.clear()
        if message_list:
            # 分片 + 指定 batch_size，避免单批过大导致超时或长事务
            batch_size = 500
            chunk_size = 1000
            total = len(message_list)
            for i in range(0, total, chunk_size):
                chunk = message_list[i : i + chunk_size]
                await with_db_timeout(
                    ChatHistory.bulk_create(chunk, batch_size=batch_size),
                    timeout=10.0,
                    operation=f"ChatHistory.bulk_create[{len(chunk)}]",
                )
            logger.debug(f"批量添加聊天记录 {total} 条", "定时任务")
    except Exception as e:
        logger.warning("存储聊天记录失败", "chat_history", e=e)
