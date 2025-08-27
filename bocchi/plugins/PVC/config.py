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
    """
    base_url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = [
        "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",
        "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",
        "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",
    ]
    model = "google/gemini-2.5-flash-image-preview:free"

advanced_config = AdvancedBuilderConfig()