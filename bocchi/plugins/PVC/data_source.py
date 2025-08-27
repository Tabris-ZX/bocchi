import requests
import json
import base64
import random
from bocchi.services.log import logger
from bocchi.utils.http_utils import AsyncHttpx
from .config import normal_config,advanced_config

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
            "response_modalities": ["TEXT", "IMAGE"]
        }
    }

    url = f"{normal_config.base_url}{normal_config.model}:generateContent?key={normal_config.api_key}"
    response = requests.post(url, headers=headers, data=json.dumps(data),verify=False)
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


async def advanced_build_pvc(img: bytes) -> bytes|int:
    """
    调用 OpenRouter(Gemini) 把用户图片转换为 PVC 手办效果图。

    Args:
        image_bytes: 输入图片的原始字节

    Returns:
        生成的图片字节；如果失败返回 None
    """
    headers = {
        "Authorization": f"Bearer {random.choice(advanced_config.api_key)}",
        "Content-Type": "application/json"
    }

    try:
        img_b64 = base64.b64encode(img).decode("utf-8")

        payload = {
            "model": "google/gemini-2.5-flash-image-preview:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": advanced_config.prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                    ],
                }
            ],
            "extra_body": {},
        }

        response = requests.post(advanced_config.base_url, headers=headers, data=json.dumps(payload))
        logger.info(f"OpenRouter PVC 状态码: {response.status_code}", "PVC")
        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            if not choices:
                return response.status_code
            message = choices[0].get("message", {})
            images = message.get("images", [])
            if not images:
                return response.status_code
            url_or_data = images[0].get("image_url", {}).get("url")
            if not url_or_data:
                return response.status_code
            if url_or_data.startswith("data:image"):
                _, encoded = url_or_data.split(",", 1)
                return base64.b64decode(encoded)
            if url_or_data.startswith("http"):
                image_bytes = await AsyncHttpx.get_content(url_or_data)
                return image_bytes
            return response.status_code
        elif response.status_code == 429:
            logger.error("OpenRouter PVC 今日额度已达上限", "PVC")
            return 429
        else:
            logger.error(f"OpenRouter PVC 请求失败: {response.status_code}", "PVC")
            return response.status_code
    except Exception as e:
        logger.error(f"OpenRouter PVC 请求异常: {e}", "PVC", e=e)
        return 500

