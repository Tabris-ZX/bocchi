
import requests
import json
import base64
import httpx  # 异步 HTTP 库，可换成你现有的 AsyncHttpx
from bocchi.services.log import logger
from .config import normal_config,img_builder_config
from typing import Optional
import io


async def normal_build_pvc(img: bytes) -> bytes | None:
    """
    构建PVC请求并返回生成的图片路径
    
    Args:
        img: 输入的图片字节数据
        
    Returns:
        str: 保存的图片文件路径，如果失败则返回空字符串
    """

    key = img_builder_config.get_api_key()
    headers = {
        "Authorization": f"Bearer {key}"
    }
    # OpenAI 兼容 images/edits 接口，multipart/form-data
    files = {
        "image": ("image.png", img, "image/png"),
    }
    data = {
        "prompt": normal_config.prompt,
        "model": img_builder_config.model,
        "response_format": "b64_json",
    }
    url = f"{img_builder_config.base_url}/images/edits"
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=120)
        logger.info(f"OpenAI兼容 Images/edits 状态码: {response.status_code}", "PVC")
        if response.status_code == 200:
            payload = response.json()
            data_list = payload.get("data") or []
            if not data_list:
                logger.error("Images/edits 响应无 data 字段", "PVC")
                return None
            b64 = data_list[0].get("b64_json")
            if not b64:
                logger.error("Images/edits 响应缺少 b64_json", "PVC")
                return None
            try:
                return base64.b64decode(b64)
            except Exception as e:
                logger.error(f"b64 解码失败: {e}", "PVC", e=e)
                return None
        elif response.status_code == 429:
            # 触发冷却
            img_builder_config.delay_key(key)
            logger.error("Images/edits 触发限流 (429)", "PVC")
            return None
        else:
            logger.error(f"Images/edits 请求失败: {response.status_code} - {response.text}", "PVC")
            return None
    except Exception as e:
        logger.error(f"Images/edits 请求异常: {e}", "PVC", e=e)
        return None

async def build_img(img: bytes, prompt: str) -> bytes | int:
    key = img_builder_config.get_api_key()
    headers = {
        "Authorization": f"Bearer {key}"
    }

    files = {
        "image": ("image.png", img, "image/png"),
    }
    data = {
        "prompt": prompt,
        "model": img_builder_config.model,
        "response_format": "b64_json",
    }
    url = f"{img_builder_config.base_url}/images/edits"
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=120)
        logger.info(f"OpenAI兼容 Images/edits 状态码: {response.status_code}", "PVC")
        if response.status_code == 200:
            payload = response.json()
            data_list = payload.get("data") or []
            if not data_list:
                logger.error("Images/edits 响应无 data 字段", "PVC")
                return 400
            b64 = data_list[0].get("b64_json")
            if not b64:
                logger.error("Images/edits 响应缺少 b64_json", "PVC")
                return 400
            try:
                return base64.b64decode(b64)
            except Exception as e:
                logger.error(f"b64 解码失败: {e}", "PVC", e=e)
                return 400
        elif response.status_code == 429:
            img_builder_config.delay_key(key)
            logger.error("Images/edits 触发限流 (429)", "PVC")
            return 429
        else:
            logger.error(f"Images/edits 请求失败: {response.status_code} - {response.text}", "PVC")
            return response.status_code
    except Exception as e:
        logger.error(f"Images/edits 请求异常: {e}", "PVC", e=e)
        return 500
