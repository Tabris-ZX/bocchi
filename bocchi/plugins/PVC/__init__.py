from nonebot_plugin_uninfo import Uninfo
from bocchi.models.user_console import UserConsole
from bocchi.plugins.PVC.data_source import advanced_build_pvc, normal_build_pvc
from bocchi.utils.enum import GoldHandle
from bocchi.utils.message import MessageUtils
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args, Arparma, At, Image, Reply, UniMessage, on_alconna
)
from nonebot_plugin_alconna.uniseg.tools import reply_fetch
from bocchi.configs.utils import PluginExtraData, RegisterConfig
from bocchi.utils.http_utils import AsyncHttpx
from bocchi.utils.platform import PlatformUtils

__plugin_meta__ = PluginMetadata(
    name="PVC",
    description="DIY手办生成/图片生成,可是有代价的!",
    usage="""
    指令:
        手办生成/pvc [图片]: 将图片变成PVC手办,每日不限次数,免费使用
        高级手办生成/ppvc [图片]: 用Gemini-2.5-flash-image-preview通道生成,每日总限额50次,每次消耗91金币

    todo:
        任意图片生成

    """.strip(),
    extra=PluginExtraData(
        author="Tabris_ZX",
        version="1.1",
        configs=[
            RegisterConfig(
                key="PVC_KEY",
                value=None,
                help="PVC接口密钥",
            ),
        ],

    ).to_dict(),
)

normal_pvc = on_alconna(
    Alconna(
        "手办生成",
        Args["image?", Image | At],
    ),
    aliases={"pvc","PVC"},
    priority=5,
    block=True,
)

advanced_pvc = on_alconna(
    Alconna(
        "高级手办生成",
        Args["image?", Image | At],
    ),
    aliases={"ppvc","PPVC"},
    priority=5,
    block=True,
)

@normal_pvc.handle()
async def handle_pvc(bot, event, params: Arparma):
    image = params.query("image") or await reply_fetch(event, bot)
    if isinstance(image, Reply) and not isinstance(image.msg, str):
        image = await UniMessage.generate(message=image.msg, event=event, bot=bot)
        for i in image:
            if isinstance(i, Image):
                image = i
                break
    if isinstance(image, Image) and image.url:
        image_bytes = await AsyncHttpx.get_content(image.url)
    elif isinstance(image, At):
        image_bytes = await PlatformUtils.get_user_avatar(image.target, "qq")
    else:
        return
    if not image_bytes:
        await UniMessage("下载图片失败QAQ...").finish(reply_to=True)
    msg = await normal_build_pvc(image_bytes)
    if msg is None:
        await MessageUtils.build_message("生成失败QAQ...").finish(reply_to=True)
    await MessageUtils.build_message(msg).finish()


@advanced_pvc.handle()
async def handle_advanced_pvc(bot, event, params: Arparma,session: Uninfo):
    user = await UserConsole.get_user(session.user.id)
    if user.gold < 91:
        await MessageUtils.build_message("你的金币不足91啦！试试普通的'手办生成'吧~").finish()
    
    image = params.query("image") or await reply_fetch(event, bot)
    if isinstance(image, Reply) and not isinstance(image.msg, str):
        image = await UniMessage.generate(message=image.msg, event=event, bot=bot)
        for i in image:
            if isinstance(i, Image):
                image = i
                break
    if isinstance(image, Image) and image.url:
        image_bytes = await AsyncHttpx.get_content(image.url)
    elif isinstance(image, At):
        image_bytes = await PlatformUtils.get_user_avatar(image.target, "qq")
    else:
        return
    if not image_bytes:
        await UniMessage("获取原始图片失败QAQ...").finish(reply_to=True)

    msg = await advanced_build_pvc(image_bytes)
    if isinstance(msg, bytes):
        await MessageUtils.build_message(msg).send()
        await UserConsole.reduce_gold(user.user_id, 91, GoldHandle.PLUGIN, "pvc")
        return

    if msg == 429:
        await MessageUtils.build_message("今日额度已达上限,试试普通的'手办生成'吧~").finish(reply_to=True)
    elif msg == 400:
        await MessageUtils.build_message("Gemini它对你沉默了,可能它不喜欢你的图片...反正肯定不是波奇的问题!").finish(reply_to=True)
    else:
        await MessageUtils.build_message(f"状态码{msg},图片生成失败,肯定不是波奇的问题!").finish(reply_to=True)
