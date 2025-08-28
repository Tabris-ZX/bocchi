from bocchi.configs.config import Config
import time
from typing import Dict, List

class NormalBuilderConfig:
    prompt = """
    把给定的照片角色变成一款 PVC 手办。  
    手办放在一个圆形透明塑料底座上，摆在画面中央。      
    在手办背后有一个半透明的塑料包装盒，盒子上印有照片里的角色图案。  
    画面要清晰表现 PVC 材质的光泽和质感。  
    背景为室内场景（如展示柜、房间或桌面），让整体效果像商品展示照。
    """

    base_url = "https://api-proxy.me/gemini/v1beta/models/"
    api_key = "AIzaSyAIHztqog_h_MEDHw_C3HvIidX1p4aAWbU"
    model = "gemini-2.0-flash-preview-image-generation"

normal_config = NormalBuilderConfig()



class AdvancedBuilderConfig:
    prompt = """
    把给定的照片角色变成一款 PVC 手办。  
    手办放在一个圆形透明塑料底座上，摆在画面中央。      
    在手办背后有一个半透明的塑料包装盒，盒子上印有照片里的角色图案。  
    画面要清晰表现 PVC 材质的光泽和质感。  
    背景为室内场景（如展示柜、房间或桌面），让整体效果像商品展示照。
    一定要生成图片给我
    (Create a PVC figurine of the character from the provided photo.
    Place the figurine on a round, transparent plastic base at the center of the scene.
    A semi-transparent plastic packaging box should be positioned behind the figurine,
    featuring the character’s image from the photo.
    Emphasize the glossy and detailed texture of the PVC material.
    Set the background as an indoor scene, such as a neatly arranged display cabinet,
    a clean tabletop, or a room, making the overall image look like a high-quality product showcase photo.
    Focus on realistic lighting, sharp details, and professional product photography style.
    Generate an image,must give me a image)
    """
    base_url = "https://openrouter.ai/api/v1/chat/completions"
    key_config = Config.get("PVC")

    # 获取 key 列表
    keys: List[str] = (
        key_config.get("PVC_KEY")
        if isinstance(key_config.get("PVC_KEY"), list)
        else [key_config.get("PVC_KEY")]
    )

    # 保存每个 key 的可用时间戳（初始都可立即使用）
    key_times: Dict[str, int] = {key: 0 for key in keys}
    cooldown_seconds = 15 * 60  # 默认每个 key 用完延迟 15 分钟

    model = "google/gemini-2.5-flash-image-preview:free"

    @classmethod
    def get_api_key(cls) -> str:
        """返回可用的 key（最早可用）"""
        now = int(time.time())
        # 按可用时间排序
        sorted_keys = sorted(cls.key_times.keys(), key=lambda k: cls.key_times[k])
        for key in sorted_keys:
            if cls.key_times[key] <= now:
                return key
        # 如果都在冷却，返回最先可用的
        return sorted_keys[0]

    @classmethod
    def delay_key(cls, key: str):
        """使用完 key 后设置冷却时间"""
        if key in cls.key_times:
            cls.key_times[key] = int(time.time()) + cls.cooldown_seconds
advanced_config = AdvancedBuilderConfig()
