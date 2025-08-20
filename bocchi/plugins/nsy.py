from random import choice, sample
from pathlib import Path
from datetime import datetime

from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Alconna, Args, on_alconna, Image as AlcImage
from nonebot_plugin_session import EventSession

from bocchi.configs.path_config import DATA_PATH
from bocchi.configs.utils import Command, PluginExtraData
from bocchi.services.log import logger
from bocchi.utils.message import MessageUtils

__plugin_meta__ = PluginMetadata(
    name="nsy图片发送",
    description="随机发送nsy图片",
    usage="""
    nsy ?[名字] ?[num=1]: 发送指定名字的图片(为空则全局随机)，num为数量
    上传 [名字] [图片]: 上传图片到指定名字的目录
    """,
    extra=PluginExtraData(
        author="Tabris_ZX",
        version="0.3",
        commands=[
            Command(command="nsy <名字>", description="发送指定名字的图片(为空则随机发送)"),
            Command(command="上传 <名字> <图片>", description="上传图片到指定名字的目录")
        ],
    ).to_dict(),
)

nsy_path: Path = DATA_PATH / "nsy"

_matcher = on_alconna(
    Alconna(
        "nsy",
        Args["name?", str, ""],
        Args["num?", int, 1],
    ),
    priority=5,
    block=True,
)

upload_matcher = on_alconna(
    Alconna(
        "上传",
        Args["name", str],
        Args["img", AlcImage]
    ),
    priority=5,
    block=True,
)

# 挑选目录下图片
valid_exts = {".png"}
def pick_images_from_dir(directory: Path, count: int) -> list[Path]:
    files = [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in valid_exts]
    if not files:
        return []
    return sample(files, min(count, len(files))) if count <= len(files) else [choice(files) for _ in range(count)]

@_matcher.handle()
async def _(name: str, num: int):
    num = max(num, 1)
    if not nsy_path.exists() or not nsy_path.is_dir():
        await MessageUtils.build_message("图片目录不存在: data/nsy").finish()

    # 获取图片列表
    img_paths: list[Path] = []
    if not name:
        # 全局随机：遍历所有子目录聚合后抽取
        all_images: list[Path] = []
        for sub in nsy_path.iterdir():
            if sub.is_dir():
                all_images.extend(p for p in sub.iterdir() if p.is_file() and p.suffix.lower() in valid_exts)
        if not all_images:
            await MessageUtils.build_message("目录中没有可用的图片: data/nsy/*").finish()
        img_paths = sample(all_images, min(num, len(all_images))) if num <= len(all_images) else [choice(all_images) for _ in range(num)]
    else:
        # 按名字包含匹配目录：当输入包含某个目录名时匹配；多个则按字典序取最前
        try:
            sub_names = [d.name for d in nsy_path.iterdir() if d.is_dir()]
        except FileNotFoundError:
            sub_names = []
        name_lower = name.lower()
        candidates = [n for n in sub_names if name_lower in n.lower()]
        if not candidates:
            await MessageUtils.build_message(f"目录中没有匹配的图片集: {name}").finish()
        name = sorted(candidates)[0]
        base_dir = nsy_path / name
        img_paths = pick_images_from_dir(base_dir, num)
        if not img_paths:
            await MessageUtils.build_message(f"目录中没有可用的图片: data/nsy/{name}").finish()

    # 发送图片
    for img_path in img_paths:
        await MessageUtils.build_message(img_path).send()

    log_name = name or "随机"
    logger.info(f"发送 nsy {log_name} 图片: {len(img_paths)} 张")

@upload_matcher.handle()
async def upload(session: EventSession, name: str, img: AlcImage):
    """上传图片到指定目录"""
    try:
        # 确保根目录存在
        nsy_path.mkdir(parents=True, exist_ok=True)
        
        # 创建或获取目标子目录
        target_dir = nsy_path / name
        target_dir.mkdir(exist_ok=True)
        
        # 生成唯一文件名（时间戳 + 随机数）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        
        # 获取图片格式，默认为PNG
        ext = ".png"  # 默认扩展名
        
        filename = f"{timestamp}_{random_suffix}{ext}"
        file_path = target_dir / filename
        
        # 保存图片
        if hasattr(img, 'raw') and img.raw:
            # 如果是二进制数据
            if isinstance(img.raw, bytes):
                with open(file_path, 'wb') as f:
                    f.write(img.raw)
            elif hasattr(img.raw, 'getvalue'):
                # BytesIO 对象
                with open(file_path, 'wb') as f:
                    f.write(img.raw.getvalue())
            else:
                await MessageUtils.build_message("无法识别的图片数据格式").finish()
                return
        elif hasattr(img, 'path') and img.path:
            # 如果是文件路径，复制文件
            import shutil
            shutil.copy2(img.path, file_path)
        elif hasattr(img, 'url') and img.url:
            # 如果是URL，下载图片
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(img.url)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
        else:
            await MessageUtils.build_message("无法识别的图片格式").finish()
            return
        
        # 验证文件是否成功保存
        if file_path.exists() and file_path.stat().st_size > 0:
            await MessageUtils.build_message(f"图片上传成功！\n保存路径: data/nsy/{name}/{filename}").send()
            logger.info(f"图片上传成功: {file_path}", "上传", session=session)
        else:
            await MessageUtils.build_message("图片上传失败，请重试").finish()
            
    except Exception as e:
        logger.error(f"图片上传失败: {e}", "上传", e=e, session=session)
        await MessageUtils.build_message(f"图片上传失败: {str(e)}").finish()
    

