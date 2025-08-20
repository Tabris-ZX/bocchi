from datetime import datetime, timedelta
import random
import json
import aiofiles
from nonebot_plugin_htmlrender import template_to_pic
from nonebot_plugin_uninfo import Uninfo
from tortoise.expressions import RawSQL
from tortoise.functions import Count

from backup.services import logger
from bocchi.configs.path_config import TEMPLATE_PATH, DATA_PATH
from bocchi.models.chat_history import ChatHistory
from bocchi.models.level_user import LevelUser
from bocchi.models.sign_user import SignUser
from bocchi.models.statistics import Statistics
from bocchi.models.user_console import UserConsole
from bocchi.utils.platform import PlatformUtils

USER_PATH = DATA_PATH / "my_info"
RACE = [
    "龙族",
    "魅魔",
    "森林精灵",
    "血精灵",
    "暗夜精灵",
    "狗头人",
    "狼人",
    "猫人",
    "猪头人",
    "骷髅",
    "僵尸",
    "虫族",
    "人类",
    "天使",
    "恶魔",
    "甲壳虫",
    "猎猫",
    "人鱼",
    "哥布林",
    "地精",
    "泰坦",
    "矮人",
    "山巨人",
    "石巨人",
]

SEX = ["男", "女"]

OCC = [
    "猎人",
    "战士",
    "魔法师",
    "狂战士",
    "魔战士",
    "盗贼",
    "术士",
    "牧师",
    "骑士",
    "刺客",
    "游侠",
    "召唤师",
    "圣骑士",
    "魔使",
    "龙骑士",
    "赏金猎手",
    "吟游诗人",
    "德鲁伊",
    "祭司",
    "符文师",
    "狂暴术士",
    "萨满",
    "裁决者",
    "角斗士",
]

lik2level = {
    2280: 8,
    1390: 7,
    840: 6,
    500: 5,
    290: 4,
    160: 3,
    80: 2,
    30: 1,
    0: 0,
}


def get_level(impression: float) -> int:
    """获取好感度等级"""
    return next((level for imp, level in lik2level.items() if impression >= imp), 0)


async def get_chat_history(
        user_id: str, group_id: str | None
) -> tuple[list[str], list[str]]:
    """获取用户聊天记录

    参数:
        user_id: 用户id
        group_id: 群id

    返回:
        tuple[list[str], list[str]]: 日期列表, 次数列表

    """
    now = datetime.now()
    filter_date = now - timedelta(days=7, hours=now.hour, minutes=now.minute)
    date_list = (
        await ChatHistory.filter(
            user_id=user_id, group_id=group_id, create_time__gte=filter_date
        )
        .annotate(date=RawSQL("DATE(create_time)"), count=Count("id"))
        .group_by("date")
        .values("date", "count")
    )
    chart_date = []
    count_list = []
    date2cnt = {str(date["date"]): date["count"] for date in date_list}
    date = now.date()
    for _ in range(7):
        if str(date) in date2cnt:
            count_list.append(date2cnt[str(date)])
        else:
            count_list.append(0)
        chart_date.append(str(date))
        date -= timedelta(days=1)
    for c in chart_date:
        chart_date[chart_date.index(c)] = c[5:]
    chart_date.reverse()
    count_list.reverse()
    return chart_date, count_list


async def get_user_info(
        session: Uninfo, user_id: str, group_id: str | None, nickname: str
) -> bytes:
    """获取用户个人信息

    参数:
        session: Uninfo
        bot: Bot
        user_id: 用户id
        group_id: 群id
        nickname: 用户昵称

    返回:
        bytes: 图片数据
    """
    platform = PlatformUtils.get_platform(session) or "qq"
    ava_url = PlatformUtils.get_user_avatar_url(user_id, platform, session.self_id)
    user = await UserConsole.get_user(user_id, platform)
    level = await LevelUser.get_user_level(user_id, group_id)
    sign_level = 0
    if sign_user := await SignUser.get_or_none(user_id=user_id):
        sign_level = get_level(float(sign_user.impression))
    chat_count = await ChatHistory.filter(user_id=user_id, group_id=group_id).count()
    stat_count = await Statistics.filter(user_id=user_id, group_id=group_id).count()
    select_index = ["" for _ in range(9)]
    select_index[sign_level] = "select"
    uid = f"{user.uid}".rjust(8, "0")
    uid = f"{uid[:4]} {uid[4:]}"
    now = datetime.now()
    weather = "moon" if now.hour < 6 or now.hour > 19 else "sun"
    chart_date, count_list = await get_chat_history(user_id, group_id)
    data = {
        "date": now.date(),
        "weather": weather,
        "ava_url": ava_url,
        "nickname": nickname,
        "title": "勇 者",
        "race": random.choice(RACE),
        "sex": random.choice(SEX),
        "occ": random.choice(OCC),
        "uid": uid,
        "description": "这是一个传奇的故事，"
                       "人类的赞歌是勇气的赞歌,人类的伟大是勇气的伟译。",
        "sign_level": sign_level,
        "level": level,
        "gold": user.gold,
        "prop": len(user.props),
        "call": stat_count,
        "say": chat_count,
        "select_index": select_index,
        "chart_date": chart_date,
        "count_list": count_list,
    }
    appoint = USER_PATH / "appointed" / f"{user_id}.json"
    if appoint.exists():
        with appoint.open("r", encoding="utf-8") as f:
            update = json.load(f)
            for key, value in update.items():
                if value != "":
                    data[key] = value

    return await template_to_pic(
        template_path=str((TEMPLATE_PATH / "my_info").absolute()),
        template_name="main.html",
        templates={"data": data},
        pages={
            "viewport": {"width": 1754, "height": 1240},
            "base_url": f"file://{TEMPLATE_PATH}",
        },
        wait=2,
    )

async def update_info(user_id: str, **update) -> bool:
    user_info = USER_PATH / "appointed" / f"{user_id}.json"
    user_info.parent.mkdir(parents=True, exist_ok=True)
    temp = {}
    if user_info.exists():
        async with aiofiles.open(user_info, mode='r', encoding='utf-8') as f:
            try:
                temp = json.loads(await f.read())
            except json.decoder.JSONDecodeError:
                logger.error("修改信息格式错误")
                return False
    else:
        create = USER_PATH / "template.json"
        async with aiofiles.open(create, mode='r', encoding='utf-8') as f:
            try:
                temp = json.loads(await f.read())
            except json.decoder.JSONDecodeError:
                logger.error("修改信息格式错误")
                return False
    temp.update(update)
    async with aiofiles.open(user_info, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(temp, ensure_ascii=False, indent=4))
        return True
