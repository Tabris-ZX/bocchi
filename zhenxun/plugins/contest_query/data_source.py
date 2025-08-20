import asyncio
import datetime
import httpx
from datetime import timedelta

from dateutil.parser import parse
from nonebot.log import logger
from typing import List, Dict
from .config import contest_config
from ...utils.message import MessageUtils

class DataSource:

    @classmethod
    def build_contest_params(cls, **kwargs) -> dict:
        """智能参数构建器"""
        now = datetime.datetime.now(datetime.timezone.utc)
        default_end = (now + timedelta(days=contest_config.days)).replace(hour=0, minute=0, second=0)
        base_params = {
            "format_time": True,
            "start__gte": now.strftime("%Y-%m-%dT%H:%M:%S"),  # 默认从当前时间开始
            "start__lte": default_end.strftime("%Y-%m-%dT%H:%M:%S"),  # 默认7天范围
            **contest_config.DEFAULT_PARAMS,
            **kwargs
        }
        return {k: v for k, v in base_params.items() if v is not None}

    @classmethod
    def build_problem_params(cls, contest_ids: int) -> dict:
        """智能参数构建器"""
        base_params = {
            **contest_config.DEFAULT_PARAMS,
            "contest_ids": {contest_ids},
            "order_by": "rating",
        }
        return {k: v for k, v in base_params.items() if v is not None}

    @classmethod
    async def get_contest(cls, **kwargs) -> List[Dict]:
        params = cls.build_contest_params(**kwargs)
        timeout = httpx.Timeout(10.0)  # 所有操作10秒超时

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://clist.by/api/v4/contest/",
                        params=params,
                    )
                    response.raise_for_status()
                    return response.json().get("objects", [])

            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"Final attempt failed: {e}")
                    await MessageUtils.build_message(
                        f"请求失败: HTTP {e.response.status_code}\n"
                        f"{e.response.text[:100]}..."
                    ).send()
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception("Unexpected error")
                await MessageUtils.build_message(
                    f"系统错误: {type(e).__name__}\n"
                    "请查看日志获取详情"
                ).send()
                break

        return []

    @classmethod
    async def get_problems(cls, contest_ids: int) -> List[Dict]:
        params = cls.build_problem_params(contest_ids)
        # 正确设置超时（四种方式任选其一）
        # 方式1：设置默认超时（推荐）
        timeout = httpx.Timeout(10.0)  # 所有操作10秒超时

        # 方式2：明确指定所有参数
        # timeout = httpx.Timeout(connect=3.0, read=15.0, write=10.0, pool=5.0)

        # 方式3：设置默认+覆盖特定参数
        # timeout = httpx.Timeout(10.0, connect=3.0)

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://clist.by/api/v4/problem/",
                        params=params,
                    )
                    response.raise_for_status()
                    return response.json().get("objects", [])

            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"Final attempt failed: {e}")
                    await MessageUtils.build_message(
                        f"请求失败: HTTP {e.response.status_code}\n"
                        f"{e.response.text[:100]}..."
                    ).send()
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception("Unexpected error")
                await MessageUtils.build_message(
                    f"系统错误: {type(e).__name__}\n"
                    "请查看日志获取详情"
                ).send()
                break

        return []

    @classmethod
    async def ans_today(cls) -> str:
        """生成今日比赛信息"""
        today_contest = await cls.get_contest(
            start__lte= (datetime.datetime.now() +
                       timedelta(days=1)).replace(hour=0, minute=0, second=0)
        )
        if not today_contest:
            logger.info("今日比赛数据为空")
            return "今天没有比赛安排哦~"
        msg_list = []
        for contest in today_contest:
            start_time = parse(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")

            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回今日 {len(msg_list)} 场比赛信息")
        return f"今日有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_recent(cls) -> str:
        """生成近期比赛信息"""
        recent_contest = await cls.get_contest()
        msg_list = []
        for contest in recent_contest:
            start_time = parse(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_contest(cls, **kwargs) -> str:
        """生成比赛信息"""
        conditions_contest = await cls.get_contest(**kwargs)
        msg_list = []
        for contest in conditions_contest:
            start_time = parse(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_problem(cls, contest_ids:int) -> str:
        """生成题目信息"""
        conditions_problem = await cls.get_problems(contest_ids)
        msg_list = []
        for problem in conditions_problem:
            msg_list.append(
                f"🏆题目名称: {problem['name']}\n"
                f"⏰题目难度: {problem['rating']}\n"
                f"📌题目ID: {problem['id']}\n"
                f"🔗题目链接: {problem.get('url', '无链接')}"
            )

        logger.info(f"返回本场比赛{len(msg_list)}条题目信息")
        return f"本场比赛有{len(msg_list)}条题目信息：\n\n" + "\n\n".join(msg_list)