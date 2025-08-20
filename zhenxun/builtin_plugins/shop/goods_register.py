import random

from backup.utils.enum import GoldHandle
from zhenxun.models.user_console import UserConsole
from zhenxun.utils.decorator.shop import shop_register


@shop_register(
    name="神秘药水",
    price=999999,
    des="鬼知道会有什么效果，要不试试？",
    partition="小秘密",
    icon="mysterious_potion.png",
)
async def _(user_id: str):
    await UserConsole.add_gold(
        user_id,
        114514,
        "shop",
    )
    return "使用道具神秘药水成功！你滴金币+114514！"

@shop_register(
    name="盲盒",
    price=100,
    des="",
    partition="",
    icon="mysterious_potion.png",
)
async def _(user_id: str):
    open = random.randint(1, 100)
    if open<49:
        if open<0.25:
            await UserConsole.reduce_gold(
                user_id,
                random.randint(1, 100),
                GoldHandle.BUY,
                "shop",
            )
        else:
            await UserConsole.add_gold(
                user_id,
                random.randint(1,200),
                "shop",
            )
    elif open<98:
        if open<0.75:
            await UserConsole

    else:
        await UserConsole.add_gold(
            user_id,
            1888,
            "shop",
        )