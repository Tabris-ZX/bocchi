from nonebot_plugin_alconna import Image
from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from urllib.parse import quote
from typing import Union, List
from httpx import Timeout


async def get_anime(anime: str) -> Union[str, List[List[Union[str, Image]]]]:
    """通过trace.moe API识别动漫截图"""
    if not anime:
        return "请输入有效的图片URL"

    try:
        # 安全编码URL
        encoded_url = quote(anime.strip())
        url = f"https://api.trace.moe/search?anilistInfo&url={encoded_url}"
        logger.debug(f"请求API: {url}")

        # 带超时的请求
        timeout = Timeout(10.0)
        response = await AsyncHttpx.get(url, timeout=timeout)
        anime_json = response.json()

        # 验证响应格式
        if not isinstance(anime_json, dict):
            return "API返回数据格式异常"
        if "error" in anime_json:
            return f"API错误: {anime_json['error']}"
        if "result" not in anime_json or not isinstance(anime_json["result"], list):
            return "未识别到动漫信息"

        # 过滤低相似度结果
        MIN_SIMILARITY = 0.5
        results = []
        for anime in anime_json["result"]:
            try:
                similarity = float(anime.get("similarity", 0))
                if similarity < MIN_SIMILARITY:
                    continue
                results.append([
                    f"名称: {anime.get('filename', '未知').rsplit('.')[0]}\n"
                    f"集数: {anime.get('episode', '未知')}\n"
                    f"相似度: {similarity * 100:.2f}%\n"
                    f"图片:",
                    Image(url=anime.get("image", "")),
                    "----------\n",
                ])
            except (KeyError, TypeError, ValueError) as e:
                logger.warning(f"解析结果失败: {e}")
                continue

        return results[:5] if results else "未匹配到高相似度结果"

    except Exception as e:
        logger.error(f"识番失败: URL={url}, 错误={str(e)}", exc_info=True)
        return "服务暂时不可用，请稍后重试"

"""
async def get_anime(anime: str) -> str | list:
    anime = anime.replace("&", "%26")
    url = f"https://api.trace.moe/search?anilistInfo&url={anime}"
    logger.debug(f"Now starting get the {url}")
    try:
        anime_json: dict = (await AsyncHttpx.get(url)).json()
        if anime_json == "Error reading imagenull":
            return "图像源错误，注意必须是静态图片哦"
        if anime_json["error"]:
            return f"访问错误 error：{anime_json['error']}"
        return [
            [
                f"名称: {anime['filename'].rsplit('.')[0]}\n"
                f"集数: {anime['episode']}\n"
                f"相似度: {float(anime['similarity'] * 100):.2f}%\n"
                f"图片:",
                Image(url=anime["image"]),
                "----------\n",
            ]
            for anime in anime_json["result"][:5]
        ]
    except Exception as e:
        logger.error("识番发生错误", e=e)
        return "发生了奇怪的错误，那就没办法了，再试一次？"
"""