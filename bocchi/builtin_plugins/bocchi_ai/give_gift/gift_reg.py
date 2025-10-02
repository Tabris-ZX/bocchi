from decimal import Decimal
import random

import nonebot
from nonebot.drivers import Driver

from bocchi.configs.config import BotConfig
from bocchi.models.sign_user import SignUser
from bocchi.models.user_console import UserConsole

from .gift_register import gift_register

driver: Driver = nonebot.get_driver()


@gift_register(
    name="可爱的钱包",
    icon="wallet.png",
    description=f"这是{BotConfig.self_nickname}的小钱包，里面装了一些金币。",
)
async def _(user_id: str):
    rand = random.randint(100, 500)
    await UserConsole.add_gold(user_id, rand, "BYM_AI")
    return f"钱包里装了{BotConfig.self_nickname}送给你的枚{rand}金币哦~"

@gift_register(
    name="完熟芒果盒子",
    icon="wallet.png",
    description=f"这是{BotConfig.self_nickname}害怕时会待的地方。",
)
async def _(user_id: str):
    rand = random.randint(100, 500)
    await UserConsole.add_gold(user_id, rand, "BYM_AI")
    return f"盒子装了{BotConfig.self_nickname}送给你的枚{rand}金币哦~"

@gift_register(
    name="Bourbon水果硬糖小发夹",
    icon="hairpin.png",
    description=f"这是{BotConfig.self_nickname}的发夹，里面是波奇对你的期望。",
)
async def _(user_id: str):
    rand = random.uniform(0.01, 0.5)
    user = await SignUser.get_user(user_id)
    user.impression += Decimal(rand)
    await user.save(update_fields=["impression"])
    return f"你使用了小发夹，{BotConfig.self_nickname}对你提升了{rand:.2f}好感度~"

@gift_register(
    name="下北泽限量版吉他拨片",
    icon="hairpin.png",
    description=f"这是{BotConfig.self_nickname}的吉他拨片",
)
async def _(user_id: str):
    rand = random.uniform(0.01, 0.5)
    user = await SignUser.get_user(user_id)
    user.impression += Decimal(rand)
    await user.save(update_fields=["impression"])
    return f"你使用了下北泽限量版吉他拨片，{BotConfig.self_nickname}对你提升了{rand:.2f}好感度~"

@driver.on_startup
async def _():
    await gift_register.load_register()
