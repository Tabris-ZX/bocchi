

from nonebot_plugin_alconna import Alconna, Args, Option, on_alconna
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from bocchi.plugins.nonebot_plungin_pkm import pkm_info

from .config import Config, pkm_config
from .pkm_merge import PkmMerge


__plugin_meta__ = PluginMetadata(
    name="宝可梦万事屋",
    description="宝可梦万事屋,支持查询宝可梦/招式/特性/道具信息,融合宝可梦等",
    usage="""
    pkm ?[宝可梦/招式/特性/道具名称] : 查询宝可梦/招式/特性/道具信息
    merge ?[宝可梦1] ?[宝可梦2] : 融合宝可梦(不填为随机)
    

    """,
    homepage="https://github.com/Tabris-ZX/nonebot-plugin-pkm.git",
    type="application",
    config=Config,
    supported_adapters={"~onebot.v11"}
)

pkm_info_matcher = on_alconna(
    Alconna(
        "pkm",
        Args["name?", str],
    ),
    priority=5,
    block=True,
)

@pkm_info_matcher.handle()
async def handle_pkm_info(name: str):
    pass



pkm_merge_matcher = on_alconna(
    Alconna(
        "merge",
        Args["name1?", str],
        Args["name2?", str],
    ),
    priority=5,
    block=True,
)

@pkm_merge_matcher.handle()
async def handle_merge_pkm(name1: str, name2: str):
    pkm_merge = PkmMerge(name1, name2)
    