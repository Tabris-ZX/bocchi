from arclet.alconna import Args, Option
from nonebot.adapters import Bot
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot_plugin_uninfo import Uninfo

from ...utils.enum import GoldHandle

from ...models.user_console import UserConsole
from .data_source import DataSource
from bocchi.configs.utils import BaseBlock, Command, PluginExtraData
from bocchi.services.log import logger
from bocchi.utils.message import MessageUtils
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Alconna, on_alconna

from bocchi.configs.path_config import DATA_PATH
from bocchi.configs.utils import PluginExtraData
from bocchi.services.log import logger
from bocchi.utils.message import MessageUtils

from nonebot_plugin_apscheduler import scheduler
from bocchi.configs.utils import PluginExtraData, Task
from bocchi.services.log import logger
from .data_source import DataSource
from ...utils.common_utils import CommonUtils
from ...utils.platform import broadcast_group
from .config import njuit_config

__plugin_meta__ = PluginMetadata(
    name="南工指北",
    description="旨在为南工院学生提供一些便捷辅助",
    usage="""
    指令:
        南工新生: 获取新生指南pdf
        南工地图: 南工院彩绘地图
        南工官网: 学校官网
        校果 ?[帖子数=10] ?[评论数=10]: 查询最新n条校果论坛帖子
        校果热榜: 查询校果论坛热榜帖子
        账号绑定 ?{宿舍}[宿舍号] ?{班级}[班级名]: 绑定qq账户和你的宿舍/班级(如果担心泄露隐私,可以私聊作者绑定) 
        电费查询: 查询已绑定宿舍的电费余额
        如: 校果 5
            账号绑定 宿舍 123456
    todo:
        电费余量不足预警
        快捷课表查询
        请假快速通知导员审批
        学生随机匹配

    还要做什么功能可以和作者提建议...
    """.strip(),
    extra=PluginExtraData(
        author="Tabris_ZX",
        version="0.4",
        tasks=[Task(module="today_xiaoguo", name="今日校果")],
    ).to_dict(),
)

NJUIT_PATH = DATA_PATH / "njuit_guide"

fm_matcher = on_alconna(
    Alconna("南工新生"),
    priority=5,
    block=True,
)
map_matcher = on_alconna(
    Alconna("南工地图"),
    priority=5,
    block=True,
)
ow_matcher = on_alconna(
    Alconna("南工官网"),
    priority=5,
    block=True,
)
bind_matcher = on_alconna(
    Alconna(
        "账号绑定",
        Option("班级", Args["class_name", str, ""]),
        Option("宿舍", Args["dorm_id", str, ""]),
    ),
    priority=5,
    block=True,
)
zx_bind_matcher = on_alconna(
    Alconna(
        "账号绑定",
        Args["user_id", str],
        Option("班级", Args["class_name", str, ""]),
        Option("宿舍", Args["dorm_id", str, ""]),
    ),
    permission=SUPERUSER,
    priority=5,
    block=True,
)
query_matcher = on_alconna(
    Alconna("电费查询"),
    priority=5,
    block=True,
)

xg_latest_matcher = on_alconna(
    Alconna(
        "校果",
        Args["tp_num?", int, njuit_config.topic_num],
        Args["cmt_num?", int, njuit_config.comment_num],
    ),
    priority=5,
    block=True,
)
xg_hot_matcher = on_alconna(
    Alconna("校果热榜"),
    priority=5,
    block=True,
)

@xg_latest_matcher.handle()
async def _(tp_num: int, cmt_num: int):
    img = await DataSource.get_topics(tp_num=tp_num, cmt_num=cmt_num,url=njuit_config.xg_latest_url)
    if not img == None:
        await MessageUtils.build_message(img).send()
    else:
        await MessageUtils.build_message("发生了一些错误,肯定不是波奇的问题!").send()
        logger.error("图片获取失败")


@xg_hot_matcher.handle()
async def handle_xg_hot():
    img = await DataSource.get_topics(tp_num=njuit_config.topic_num,cmt_num=njuit_config.comment_num,url=njuit_config.xg_hot_url)
    if not img == None:
        await MessageUtils.build_message(img).send()
    else:
        await MessageUtils.build_message("发生了一些错误,肯定不是波奇的问题!").send()
        logger.error("图片获取失败")


@fm_matcher.handle()
async def handle_fm_match():
    pdf_path = NJUIT_PATH / "freshman.pdf"
    msg = await DataSource.send_file(pdf_path, "南工院新生宝典")
    await fm_matcher.finish(msg)


@map_matcher.handle()
async def handle_send_image():
    # 构建完整图片路径
    map_path = NJUIT_PATH / "map.png"
    await MessageUtils.build_message(map_path).send()


@ow_matcher.handle()
async def handle_send_ow():
    await MessageUtils.build_message("https://www.niit.edu.cn/").send()


@bind_matcher.handle()
async def handle_bind(session: Uninfo, class_name: str = "", dorm_id: str = ""):
    # 检查是否提供了必要的参数
    user = await UserConsole.get_user(session.user.id)
    if user.gold < 100:
        await MessageUtils.build_message("金币不足！").finish()
    if not class_name and not dorm_id:
        await MessageUtils.build_message(
            "请提供班级或宿舍信息！\n使用教程:请发送'波奇帮助91'"
        ).send(reply_to=True)
        return

    # 仅使用 user_id 进行绑定
    bind = await DataSource.bind_info(
        user_id=session.user.id, class_name=class_name, dorm_id=dorm_id
    )
    logger.info(
        f"绑定结果: 用户ID: {session.user.id}, 班级: {class_name}, 宿舍: {dorm_id}"
    )
    if bind:
        await UserConsole.reduce_gold(user.user_id, 100, GoldHandle.BUY, "niit_guide")
        await MessageUtils.build_message("绑定成功!").send(reply_to=True)
    else:
        await MessageUtils.build_message("绑定失败,肯定不是波奇的问题!").send(
            reply_to=True
        )


@zx_bind_matcher.handle()
async def handle_zx_bind(user_id: str, class_name: str = "", dorm_id: str = ""):
    bind = await DataSource.bind_info(
        user_id=user_id, class_name=class_name, dorm_id=dorm_id
    )
    logger.info(f"绑定结果: 用户ID: {user_id}, 班级: {class_name}, 宿舍: {dorm_id}")
    if bind:
        await MessageUtils.build_message("绑定成功!").send(reply_to=True)
    else:
        await MessageUtils.build_message("绑定失败,肯定不是波奇的问题!").send(
            reply_to=True
        )


@query_matcher.handle()
async def handle_query(session: Uninfo):
    msg = await DataSource.query_balance(session.user.id)
    await MessageUtils.build_message(msg).send(reply_to=True)


# 每日定时任务
async def check(bot: Bot, group_id: str) -> bool:
    return not await CommonUtils.task_is_block(bot, "today_xiaoguo", group_id)

@scheduler.scheduled_job(
    "cron",
    hour=12,
    minute=1,
)
async def send_daily_xg():
    try:
        img = await DataSource.get_topics(tp_num=njuit_config.topic_num,cmt_num=njuit_config.comment_num,url=njuit_config.xg_latest_url)
        if img == None:
            logger.error("图片获取失败")
            return
        msg = MessageUtils.build_message(img)
        await broadcast_group(
            msg,
            log_cmd="今日校果",  # 修改日志标识
            check_func=check,  # 保留检查函数
        )
        logger.info("每日校果提醒发送成功")
    except Exception as e:
        logger.error(f"发送每日校果提醒失败: {e}")
