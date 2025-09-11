import datetime

from nonebot.internal.adapter import Bot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    on_alconna,
)
from nonebot_plugin_apscheduler import scheduler

from bocchi.configs.utils import PluginExtraData, Task
from bocchi.services.log import logger

from ...utils.common_utils import CommonUtils
from ...utils.platform import broadcast_group
from .config import contest_config
from .data_source import DataSource

__plugin_meta__ = PluginMetadata(
    name="算竞日程查询",
    description="查询全球各大在线OJ的算法比赛信息",
    usage="""
    指令:
        今日?{比赛}: 获取今日还未进行的全球OJ比赛(有每日定时播报)
        近期?{比赛}: 获取近期还未进行的全球OJ比赛
        比赛 ?[平台id] ?[日期=7]: 检索指定条件的OJ比赛
        clt/官网: 打开clist官网
    todo:
        提醒 ?[比赛id]: 在指定id/今日所有的比赛开始前提醒
        取消 ?[比赛id]: 取消指定id/所有比赛提醒
        题目 ?[分类] ?[难度]: 获取指定条件的随机题目
    部分resource_id对应: CodeForces: 1
                    AtCoder: 93
                    LeetCode: 102
                    LuGuo: 162
                    NewCoder: 166
    """.strip(),
    extra=PluginExtraData(
        author="Tabris_ZX",
        version="1.0",
        # tasks=[Task(module="today_match", name="今日算法比赛")],
    ).to_dict(),
)

# 查询全部比赛
recent_contest = on_alconna(
    Alconna("近期比赛"),
    aliases={"近期"},
    priority=5,
    block=True,
)


@recent_contest.handle()
async def handle_all_matcher():
    msg = await DataSource.ans_recent()
    await recent_contest.finish(msg)


# 查询今日比赛
query_today_contest = on_alconna(
    Alconna("今日比赛"),
    aliases={"今日"},
    priority=5,
    block=True,
)


@query_today_contest.handle()
async def handle_today_match():
    msg = await DataSource.ans_today()
    await query_today_contest.finish(msg)


# 按条件检索比赛
query_conditions_contest = on_alconna(
    Alconna("比赛", Args["resource_id?", int], Args["days?", int]),
    priority=5,
    block=True,
)


@query_conditions_contest.handle()
async def handle_match_id_matcher(
    resource_id: int,
    days: int = contest_config.days,
):
    end_time = (datetime.datetime.now() + datetime.timedelta(days=days)).replace(
        hour=0, minute=0, second=0
    )
    msg = await DataSource.ans_conditions_contest(
        resource_id=resource_id, end__lte=end_time
    )
    await query_conditions_contest.finish(msg)


query_conditions_problem = on_alconna(
    Alconna(
        "题目",
        Args["contest_ids", int],
    ),
    priority=5,
    block=True,
)


@query_conditions_problem.handle()
async def handle_problem_matcher(
    contest_ids: int,
):
    msg = await DataSource.ans_conditions_problem(contest_ids)
    await query_conditions_problem.finish(msg)


clist = on_alconna(
    Alconna("clt"),
    aliases={"官网"},
    priority=5,
    block=True,
)


@clist.handle()
async def handle_clist_matcher():
    msg = "https://clist.by/"
    await clist.finish(msg)


remind_matches = on_alconna(
    Alconna(
        "提醒",
        Args["id?", int],
    ),
    priority=5,
    block=True,
)

# 每日定时任务
async def check(bot: Bot, group_id: str) -> bool:
    return not await CommonUtils.task_is_block(bot, "today_match", group_id)


@scheduler.scheduled_job(
    "cron",
    hour=6,  # 改为凌晨0点
    minute=1,  # 第1分钟
)
async def send_daily_matches():
    try:
        msg = await DataSource.ans_today()
        await broadcast_group(
            msg,
            log_cmd="今日比赛提醒",  # 修改日志标识
            check_func=check,  # 保留检查函数
        )
        logger.info("每日比赛提醒发送成功")
    except Exception as e:
        logger.error(f"发送每日比赛提醒失败: {e}")
