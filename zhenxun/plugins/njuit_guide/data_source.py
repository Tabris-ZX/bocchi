import base64
from pathlib import Path
import re
from nonebot.adapters.onebot.v11 import Message,MessageSegment
from .config import njuit_config
from .model import NjuitStu
from zhenxun.configs.path_config import DATA_PATH
from zhenxun.services.log import logger
from pathlib import Path
from typing import Optional
import httpx
from datetime import datetime
from nonebot import logger
from playwright.async_api import async_playwright, expect
from html import escape
from typing import Optional
from zhenxun.services.db_context import Model

NJUIT_PATH = DATA_PATH / "njuit_guide"
save_path = NJUIT_PATH / "xiaoguo.png"
save_path.parent.mkdir(parents=True, exist_ok=True)
xg_path = NJUIT_PATH / "xg_template.html"
xg_path.parent.mkdir(parents=True, exist_ok=True)


class DataSource:
    # 时间格式化函数
    @classmethod
    async def format_time(cls,full_time_str):
        try:
            dt = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%m-%d %H:%M")
        except:
            return full_time_str

    @classmethod
    async def html_to_img(cls, html_content: str, output_path: Path = save_path) -> bool:
        browser = None
        try:
            async with async_playwright() as p:
                # 关键修改1：启动浏览器时模拟移动设备
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 375, "height": 812},  # 保持字典形式
                    device_scale_factor=2,
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
                )
                page = await context.new_page()
                
                # 关键修改2：确保传递的 HTML 包含完整的移动端 meta 标签
                if not isinstance(html_content, str):
                    html_content = str(html_content)
                
                # 强制注入移动端 meta 标签（如果原 HTML 没有）
                if "<meta name=\"viewport\"" not in html_content:
                    html_content = html_content.replace(
                        "<head>", 
                        "<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no\">"
                    )
                
                await page.set_content(
                    html_content,
                    timeout=10_000,
                    wait_until="networkidle"
                )
                
                # 关键修改3：截图时捕获完整高度
                await page.screenshot(
                    path=str(output_path),
                    full_page=True,
                    type="jpeg",
                    quality=90,  # 可选：提高图片质量
                    timeout=15_000
                )
                return True
        except Exception as e:
            logger.error(f"截图失败: {type(e).__name__}: {e}", exc_info=True)
            return False
        finally:
            if browser:
                await browser.close()

    @classmethod
    async def get_topics(cls,tp_num:int,cmt_num:int,url:str) -> Optional[Path]:
        try:
            # 使用列表高效收集HTML片段
            html_template = xg_path.read_text(encoding="utf-8")
            html_parts = [html_template]
            async with httpx.AsyncClient(headers=njuit_config.xg_headers, timeout=30.0) as client:
                # 获取话题数据
                response = await client.get(f"{url}")
                response_data = response.json().get("data", {})
                
                # 根据不同的 API 响应结构处理数据
                if isinstance(response_data, list):
                    # 如果 data 直接是数组（如 xg_hot_url）
                    data = response_data[:tp_num]
                elif isinstance(response_data, dict):
                    # 如果 data 是字典，尝试获取 rows 字段
                    data = response_data.get("rows", [])[:tp_num]
                else:
                    data = []

                for topic in data:
                    # 安全转义所有用户输入
                    content = escape(topic.get("content", ""))
                    time_str = await cls.format_time(topic.get("createTime", ""))
                    
                    # 构建HTML块
                    html_parts.append(f"""
                    <div class="topic">
                        <div class="topic-title">📌 {content}</div>
                        <div class="topic-meta">
                            <span class="icon">🕒</span>
                            <span>{time_str}</span>
                        </div>
                    """)
                    
                    # 处理图片
                    if imgs := topic.get("imgs"):
                        html_parts.append('<div class="topic-images">')
                        html_parts.extend(
                            f'<img src="{escape(img_url)}" alt="帖子图片" loading="lazy">'
                            for img_url in imgs
                        )
                        html_parts.append('</div>')
                    
                    # 处理评论
                    try:
                        comments_url = f"{njuit_config.xg_comments_url}?topic_id={topic['id']}&sort=hot&page=1"
                        comments_response = await client.get(comments_url)
                        comments_response.raise_for_status()  # 检查 HTTP 状态码
                        comments_data = comments_response.json().get("data", {})
                        
                        # 根据不同的 API 响应结构处理评论数据
                        if isinstance(comments_data, list):
                            # 如果 data 直接是数组
                            comments = comments_data[:cmt_num]
                        elif isinstance(comments_data, dict):
                            # 如果 data 是字典，尝试获取 rows 字段
                            comments = comments_data.get("rows", [])[:cmt_num]
                        else:
                            comments = []
                        
                        # 添加调试日志
                        logger.debug(f"话题 {topic.get('id', 'unknown')} 评论 URL: {comments_url}")
                        logger.debug(f"评论响应状态: {comments_response.status_code}")
                        logger.debug(f"评论数据: {comments_data}")
                        logger.debug(f"解析后评论数量: {len(comments)}")
                        
                    except Exception as e:
                        logger.warning(f"获取话题 {topic.get('id', 'unknown')} 的评论失败: {e}")
                        comments = []
                    
                    if comments:
                        html_parts.append('<div class="comments-section">')
                        for comment in comments:
                            # 评论内容
                            comment_content = escape(comment.get("content", ""))
                            comment_time = await cls.format_time(comment.get("createTime", ""))
                            user_nickname = escape(comment.get("userInfo", {}).get("nickname", "匿名用户"))
                            
                            html_parts.append(f'''
                            <div class="comment">
                                <div class="comment-header">
                                    <span class="icon">💬</span>
                                    <span class="comment-author">{user_nickname}</span>
                                    <span class="comment-time">{comment_time}</span>
                                </div>
                                <div class="comment-content">{comment_content}</div>
                            ''')
                            
                            # 处理评论图片
                            if comment_imgs := comment.get("imgs"):
                                html_parts.append('<div class="comment-images">')
                                html_parts.extend(
                                    f'<img src="{escape(img_url)}" alt="评论图片" loading="lazy">'
                                    for img_url in comment_imgs
                                )
                                html_parts.append('</div>')
                            
                            # 处理评论回复
                            replys_data = comment.get("replys", {})
                            if isinstance(replys_data, dict) and replys_data.get("rows"):
                                # 如果 replys 是字典且有 rows 字段
                                replys = replys_data["rows"]
                                html_parts.append('<div class="replies-section">')
                                for reply in replys:
                                    reply_content = escape(reply.get("content", ""))
                                    reply_time = await cls.format_time(reply.get("createTime", ""))
                                    reply_nickname = escape(reply.get("userInfo", {}).get("nickname", "匿名用户"))
                                    
                                    html_parts.append(f'''
                                    <div class="reply">
                                        <div class="reply-header">
                                            <span class="icon">↩️</span>
                                            <span class="reply-author">{reply_nickname}</span>
                                            <span class="reply-time">{reply_time}</span>
                                        </div>
                                        <div class="reply-content">{reply_content}</div>
                                    ''')
                                    
                                    # 处理回复图片
                                    if reply_imgs := reply.get("imgs"):
                                        html_parts.append('<div class="reply-images">')
                                        html_parts.extend(
                                            f'<img src="{escape(img_url)}" alt="回复图片" loading="lazy">'
                                            for img_url in reply_imgs
                                        )
                                        html_parts.append('</div>')
                                    
                                    html_parts.append('</div>')  # 关闭reply div
                                
                                html_parts.append('</div>')  # 关闭replies-section div
                            elif isinstance(replys_data, list):
                                # 如果 replys 直接是列表
                                replys = replys_data
                                if replys:
                                    html_parts.append('<div class="replies-section">')
                                    for reply in replys:
                                        reply_content = escape(reply.get("content", ""))
                                        reply_time = await cls.format_time(reply.get("createTime", ""))
                                        reply_nickname = escape(reply.get("userInfo", {}).get("nickname", "匿名用户"))
                                        
                                        html_parts.append(f'''
                                        <div class="reply">
                                            <div class="reply-header">
                                                <span class="icon">↩️</span>
                                                <span class="reply-author">{reply_nickname}</span>
                                                <span class="reply-time">{reply_time}</span>
                                            </div>
                                            <div class="reply-content">{reply_content}</div>
                                        ''')
                                        
                                        # 处理回复图片
                                        if reply_imgs := reply.get("imgs"):
                                            html_parts.append('<div class="reply-images">')
                                            html_parts.extend(
                                                f'<img src="{escape(img_url)}" alt="回复图片" loading="lazy">'
                                                for img_url in reply_imgs
                                            )
                                            html_parts.append('</div>')
                                        
                                        html_parts.append('</div>')  # 关闭reply div
                                    
                                    html_parts.append('</div>')  # 关闭replies-section div
                            
                            html_parts.append('</div>')  # 关闭comment div
                        
                        html_parts.append('</div>')  # 关闭comments-section div
                    
                    html_parts.append("</div>")  # 关闭topic div
            # 合并HTML
            html_parts.append("</body></html>")
            full_html = "".join(html_parts)
            
            # 生成图片
            if await cls.html_to_img(full_html):
                return save_path
            return None

        except Exception as e:
            logger.error(f"生成失败: {type(e).__name__}: {e}", exc_info=True)
            return None
    
    @classmethod
    async def send_file(cls,file_path: Path, file_type: str):
        """文件发送函数"""
        try:
            abs_path = file_path.absolute()
            # 详细路径检查
            if not abs_path.exists():
                available_files = "\n".join([f.name for f in NJUIT_PATH.glob("*")])
                logger.error(f"文件不存在，目录内容：\n{available_files}")
                return f"❌ {file_type}文件不存在（路径：{abs_path}）"
            if file_path.suffix == ".pdf":
                with open(abs_path, "rb") as f:
                    file_base64 = base64.b64encode(f.read()).decode()
                return Message(f"[CQ:file,file=base64://{file_base64},name={file_path.name}]")
            else:
                # 使用file uri格式
                return MessageSegment.image(f"file:///{abs_path}")
        except Exception as e:
            logger.error(f"发送{file_type}失败")
            return f"❌ {file_type}发送失败：{str(e)}"

    @classmethod
    async def bind_info(cls, user_id, class_name=None, dorm_id=None) -> bool:
        try:
            # 过滤空字符串，转换为None
            class_name = class_name if class_name else None
            dorm_id = dorm_id if dorm_id else None
            
            # 仅使用 user_id 作为键
            await NjuitStu.update_or_create(
                user_id=user_id,
                defaults={
                    'class_name': class_name,
                    'dorm_id': dorm_id
                }
            )
            logger.info(f"绑定信息成功: user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"绑定信息失败: {e}")
            return False

    @classmethod
    async def query_balance(cls, user_id) -> str:
        try:
            data = await NjuitStu.get_data(user_id=user_id)
            if not data or not getattr(data, "dorm_id", None):
                return "你还没有绑定宿舍捏~ 发送'波奇帮助91'查看绑定方法吧~"
            async with httpx.AsyncClient(headers=njuit_config.bill_header, timeout=30.0) as client:
                response = await client.get(f"{njuit_config.bill_url}roomAccountID={data.dorm_id}")
                response.raise_for_status()  # 检查 HTTP 状态码
                html = response.text
                # 更健壮的正则匹配
                balance_match = re.search(
                    r'可用余额</label>\s*<span class="weui-form-preview__value">([^<]+)',
                    html
                )
                if not balance_match:
                    logger.error("电费页面结构可能已变更，无法解析余额")
                    return "宿舍不存在，请检查绑定后后再试~"

                return "你宿舍的电费余额为"+balance_match.group(1).strip()

        except httpx.HTTPError as e:
            logger.error(f"请求电费接口失败: {type(e).__name__}: {e}")
            return "网络开小差了，请稍后再试~"
        except Exception as e:
            logger.error(f"获取电费失败: {type(e).__name__}: {e}", exc_info=True)
            return "获取电费时发生错误，请联系管理员~"