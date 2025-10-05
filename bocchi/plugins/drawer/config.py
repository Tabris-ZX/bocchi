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

    # 使用 OpenAI 兼容接口，由 ImgBuilderConfig 统一提供 base_url / model / api_key

normal_config = NormalBuilderConfig()

class ImgBuilderConfig:
    pvc_prompt = """
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
    ntr_prompt = """
        A cinematic scene inside a fast food
        restaurant at night.
        Foreground: a lonely table with burgers
        and fries, and a smartphone shown large
        and sharp on the table, clearly displaying
        the uploaded anime/game character
        image.
        A hand is reaching for food, symbolizing
        solitude.
        Midground: in the blurred background, a
        couple is sitting together and kiss.
        One of them is represented as a
        cosplayer version of the uploaded
        character:
        -If the uploaded character is humanoid,
        show accurate cosplay with hairstyle,
        costume, and signature props.
        -If the uploaded character is
        non-humanoid (mecha, creature, mascot,
        etc.), show a gijinka (humanized cosplay
        interpretation) that carries clear visual
        cues, costume colors, and props from the
        reference image (armor pieces, wings,
        ears, weapon, or iconic accessories).
        The other person is an ordinary japan
        human, and they are showing intimate
        affection (kissing, holding hands, or
        sharing food).
        Background: large glass windows, blurred
        neon city lights outside.
        Mood: melancholic, bittersweet, ironic,
        cinematic shallow depth of field.
        [reference: the uploaded image defines
        both the smartphone display and the
        cosplay design, with visible props
        emphasized]
        Image size is 585px 1024px
    """
    key_config = Config.get("PVC")
    base_url = key_config.get("PVC_BASE_URL") or "https://api.openai.com/v1"

    #多key轮询
    keys: List[str] = (
        key_config.get("PVC_KEY")
        if isinstance(key_config.get("PVC_KEY"), list)
        else [key_config.get("PVC_KEY")]
    )
    key_times: Dict[str, int] = {key: 0 for key in keys}
    cooldown_seconds = 15 * 60  

    model = key_config.get("PVC_MODEL") or "gpt-image-1"

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
img_builder_config = ImgBuilderConfig()
