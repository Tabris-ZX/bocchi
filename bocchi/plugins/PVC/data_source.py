from time import sleep
import requests
import json
import base64
import httpx  # 异步 HTTP 库，可换成你现有的 AsyncHttpx
from bocchi.services.log import logger
from bocchi.utils.http_utils import AsyncHttpx
from .config import normal_config,advanced_config

from PIL import Image
import io
import base64

# def compress_image(img_bytes: bytes,max_size=(2048, 2048),target_kb=1024,min_quality=50) -> str:
#     """
#     将任意图片 bytes 压缩到 Gemini 2.5 可接受的大小，并返回 Base64 字符串。

#     参数:
#         img_bytes: 原始图片 bytes
#         max_size: 最大宽高 (width, height)
#         target_kb: 压缩目标大小，KB
#         min_quality: 最低 JPEG 质量

#     返回:
#         base64 字符串，可直接用于 image_url
#     """
#     with Image.open(io.BytesIO(img_bytes)) as img:
#         img.thumbnail(max_size)
#         quality = 90
#         output = io.BytesIO()
#         img.save(output, format="JPEG", quality=quality)
#         data = output.getvalue()

#         # 循环压缩直到小于目标大小或达到最小质量
#         while len(data) > target_kb * 1024 and quality > min_quality:
#             quality -= 5
#             output = io.BytesIO()
#             img.save(output, format="JPEG", quality=quality)
#             data = output.getvalue()

#         return base64.b64encode(data).decode("utf-8")



async def normal_build_pvc(img: bytes) -> bytes|None:
    """
    构建PVC请求并返回生成的图片路径
    
    Args:
        img: 输入的图片字节数据
        
    Returns:
        str: 保存的图片文件路径，如果失败则返回空字符串
    """

    headers = {
        "Content-Type": "application/json"
    }    
    data = {
        "contents": [{
            "parts": [{"text": normal_config.prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": base64.b64encode(img).decode("utf-8")
                        }
                    },
                    ]
        }],
        "generation_config": {
            "response_modalities": ["IMAGE"]
        }
    }

    url = f"{normal_config.base_url}{normal_config.model}:generateContent?key={normal_config.api_key}"
    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"PVC API请求状态码: {response.status_code}", "PVC")

    # 检查响应状态
    if response.status_code == 200:
        response_json = response.json()
        logger.info("PVC API调用成功！", "PVC")

        # 正确解析响应结构
        if "candidates" in response_json and response_json["candidates"]:
            candidate = response_json["candidates"][0]

            if "content" in candidate and "parts" in candidate["content"]:
                text_response = ""
                image_data = None

                # 遍历所有parts来查找文本和图片数据
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        text_response = part["text"]
                        logger.info(f"PVC API返回文本描述: {text_response}", "PVC")

                    if "inlineData" in part:
                        try:
                            # 解码base64图片数据
                            image_data_base64 = part["inlineData"]["data"]
                            image_data = base64.b64decode(image_data_base64)
                            logger.info("成功获取PVC API图片数据", "PVC")
                        except Exception as e:
                            logger.error(f"PVC API图片解码失败: {e}", "PVC", e=e)
                            image_data = None
                return image_data
            else:
                logger.error("PVC API响应中没有content或parts字段", "PVC")
                return None
        else:
            logger.error("PVC API响应中没有candidates字段", "PVC")
            return None

    else:
        logger.error(f"PVC API请求失败，状态码: {response.status_code}", "PVC")
        logger.error(f"PVC API错误信息: {response.text}", "PVC")
        return None

async def advanced_build_pvc(img: bytes) -> bytes | int:
    headers = {
        "Authorization": f"Bearer {advanced_config.get_api_key()}",
        "Content-Type": "application/json"
    }

    if isinstance(img, bytes):
        img_data = base64.b64encode(img).decode("utf-8")
        image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}

    payload = {
        "model": "google/gemini-2.5-flash-image-preview:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": advanced_config.prompt},
                    image_content
                ],
            }
        ],
        "extra_body": {}
    }
    try:
        response = requests.post(advanced_config.base_url, headers=headers, json=payload)
        logger.info(f"OpenRouter 状态码: {response.status_code}", "PVC")
        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            for choice in choices:
                images = choice.get("message", {}).get("images", [])
                # 遍历所有images
                for image in images:
                    url = image.get("image_url", {}).get("url")
                    try:
                        if url.startswith("data:image"):
                            # Base64 图片
                            _, encoded = url.split(",", 1)
                            return base64.b64decode(encoded)
                        elif url.startswith("http"):
                            # 网络 URL 下载
                            async with httpx.AsyncClient(timeout=60) as client:
                                r = await client.get(url)
                                r.raise_for_status()
                                return r.content
                        else:
                            logger.error(f"未知图片 URL 格式", "PVC")
                            continue
                    except Exception as e:
                        logger.error(f"处理图片失败: {e}", "PVC", e=e)
                        continue
            
            # 如果所有choices和images都处理完但没有返回，说明没有有效图片
            logger.error(f"OpenRouter 没有找到有效的图片数据,result:{result}", "PVC")
            return 400

        elif response.status_code == 429:
            logger.error("OpenRouter今日额度已达上限", "PVC")
            return 429
        else:
            logger.error(f"OpenRouter 请求失败: {response.status_code}", "PVC")
            return response.status_code

    except Exception as e:
        logger.error(f"OpenRouter 请求异常: {e}", "PVC", e=e)
        return 500
