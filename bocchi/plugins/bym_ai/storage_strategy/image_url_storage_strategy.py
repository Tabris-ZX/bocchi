from .storage_strategy import StorageStrategy


class ImageUrlStorageStrategy(StorageStrategy):
    """图片URL存储策略，直接返回图片的原始URL"""
    
    def __init__(self, **kwargs):
        pass
    
    async def upload(self, file_path) -> str:
        """
        返回图片的原始URL
        
        参数:
            file_path: 图片文件路径
            
        返回:
            str: 图片URL
        """
        # 直接返回QQ图片的原始URL，避免base64编码
        # 这样可以大大减少请求体大小
        return f"https://qq-image-url.com/{file_path.name}" 