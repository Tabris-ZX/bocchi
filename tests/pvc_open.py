import os
import requests
import base64
import json

API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# 读取本地图片并编码为 base64
with open("/home/zx/bot/bocchi/tests/t.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "google/gemini-2.5-flash-image-preview:free",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """把给定的照片角色变成一款 PVC 手办。  
手办放在一个圆形透明塑料底座上，摆在画面中央。  
在手办背后有一个半透明的塑料包装盒，盒子上印有照片里的角色图案。  
画面要清晰表现 PVC 材质的光泽和质感。  
背景为室内场景（如展示柜、房间或桌面），让整体效果像商品展示照。"""
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                }
            ]
        }
    ],
    "extra_body": {}
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

resp = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))

if resp.status_code != 200:
    print("请求失败:", resp.status_code, resp.text)
    exit(1)

result = resp.json()

# 递归打印 JSON 字段名
def print_keys(data, indent=0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{prefix}{key}")
            print_keys(value, indent + 1)
    elif isinstance(data, list):
        for item in data:
            print_keys(item, indent + 1)

print_keys(result)


def download_images_from_result(result, save_dir="."):
    """
    从 OpenAI / OpenRouter chat completion 的 result 中下载所有图片。
    图片会保存到 save_dir（默认为当前目录）。
    支持 base64 和 URL。
    """
    for choice_idx, choice in enumerate(result.get("choices", [])):
        message = choice.get("message", {})
        images = message.get("images", [])
        for idx, image in enumerate(images):
            url_or_data = image.get("image_url", {}).get("url")
            if not url_or_data:
                continue
            try:
                if url_or_data.startswith("data:image"):
                    # Base64 图片
                    _, encoded = url_or_data.split(",", 1)
                    img_data = base64.b64decode(encoded)
                    file_path = os.path.join(save_dir, f"result_{choice_idx}_{idx}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(img_data)
                    print(f"图片已保存为 {file_path}")
                elif url_or_data.startswith("http"):
                    # 网络 URL 下载
                    r = requests.get(url_or_data)
                    r.raise_for_status()
                    file_path = os.path.join(save_dir, f"result_{choice_idx}_{idx}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(r.content)
                    print(f"图片已下载保存为 {file_path}")
            except Exception as e:
                print(f"下载第 {choice_idx}-{idx} 张图片失败: {e}")

download_images_from_result(result)