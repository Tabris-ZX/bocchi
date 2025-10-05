import re
import httpx
import asyncio
from pathlib import Path
from typing import Optional

from nonebot import get_bot
from bocchi import ui

from bocchi.configs.path_config import DATA_PATH, THEMES_PATH
from bocchi.services.log import logger
from nonebot_plugin_uninfo import get_interface

from .config import njuit_config
from .model import NjuitStu


FILE_PATH = DATA_PATH / "njuit_guide"
TEMPLATES_PATH = THEMES_PATH / "default" / "templates" /"pages"/"builtin"/ "njuit_guide"


class ElectricityService:
    """电费相关服务类"""

    @classmethod
    def _generate_user_html(cls, user: dict) -> str:
        """生成单个用户的HTML"""
        avatar_html = f'<img src="{user.get("avatar", "")}" class="user-avatar" onerror="this.style.display=\'none\'">' if user.get('avatar') else ''
        
        if user['error']:
            return f'''
            <div class="user-item error-item">
                <div class="user-info">
                    {avatar_html}
                    <div class="user-name">{user['name']}</div>
                </div>
                <div class="balance-info">
                    <span class="balance-label">电费余额</span>
                    <span class="balance-amount error-amount">{user['balance']}</span>
                </div>
            </div>
            '''
        
        # 根据余额判断样式
        balance_class = "high" if user['value'] >= 50 else "medium" if user['value'] >= 20 else "low"
        
        return f'''
        <div class="user-item">
            <div class="user-info">
                {avatar_html}
                <div class="user-name">{user['name']}</div>
            </div>
            <div class="balance-info">
                <span class="balance-label">电费余额</span>
                <span class="balance-amount {balance_class}">{user['balance']}</span>
            </div>
        </div>
        '''

    @classmethod
    async def _get_electricity_balance(cls, dorm_id: str) -> dict:
        """获取宿舍电费余额信息"""
        try:
            async with httpx.AsyncClient(headers=njuit_config.bill_header, timeout=30.0) as client:
                response = await client.get(f"{njuit_config.bill_url}roomAccountID={dorm_id}")
                response.raise_for_status()
                html = response.text
                
                balance_match = re.search(
                    r'可用余额</label>\s*<span class="weui-form-preview__value">([^<]+)',
                    html
                )
                
                if balance_match:
                    balance_raw = balance_match.group(1).strip()
                    try:
                        match = re.search(r'[\d.]+', balance_raw)
                        if match:
                            balance_value = float(match.group())
                            return {
                                'balance': f"{balance_value:.2f}元",
                                'value': balance_value,
                                'error': False
                            }
                    except ValueError:
                        pass
                    return {'balance': balance_raw, 'value': 0, 'error': False}
                else:
                    return {'balance': '查询失败', 'value': 0, 'error': True}
                    
        except Exception as e:
            logger.error(f"查询宿舍 {dorm_id} 电费失败: {e}")
            return {'balance': '查询失败', 'value': 0, 'error': True}
    
    @classmethod
    async def validate_dorm_id(cls, dorm_id: str) -> bool:
        """验证宿舍ID是否有效（能正常查询电费）"""
        balance_info = await cls._get_electricity_balance(dorm_id)
        return not balance_info['error']

    @classmethod
    async def bind_info(cls, user_id, class_name=None, dorm_id=None) -> bool:
        """绑定用户信息（包含宿舍验证）"""
        try:
            # 过滤空字符串，转换为None
            class_name = class_name if class_name else None
            dorm_id = dorm_id if dorm_id else None
            
            # 如果提供了宿舍ID，先验证宿舍是否有效
            if dorm_id:
                if not await cls.validate_dorm_id(dorm_id):
                    logger.warning(f"宿舍 {dorm_id} 验证失败，无法查询电费余额")
                    return False
            
            # 仅使用 user_id 作为键
            await NjuitStu.update_or_create(
                user_id=user_id,
                defaults={
                    'class_name': class_name,
                    'dorm_id': dorm_id,
                    'push': True
                }
            )
            logger.info(f"绑定信息成功: user_id={user_id}, dorm_id={dorm_id}")
            return True
        except Exception as e:
            logger.error(f"绑定信息失败: {e}")
            return False

    @classmethod
    async def query_balance(cls, user_id):
        """查询用户宿舍电费余额"""
        data = await NjuitStu.get_data(user_id=user_id)
        if not data or not data.dorm_id:
            dorm_id_path = FILE_PATH/"dorm_id.png"
            return ["你还没有绑定宿舍捏~ \n私聊小波奇发送\n账号绑定  dorm  宿舍id\n来绑定宿舍吧~",dorm_id_path]
        
        balance_info = await cls._get_electricity_balance(data.dorm_id)
        if balance_info['error']:
            return "网络开小差了，请稍后再试~"
        
        return f"你宿舍的电费还有{balance_info['balance']}呢"

    @classmethod
    async def get_daily_electricity_reminder_for_group(cls, group_id: str) -> Optional[Path]:
        """获取指定群组的电费提醒消息内容"""
        try:
            bot = get_bot()
            # 获取群中开启推送的用户
            group_members = await bot.get_group_member_list(group_id=int(group_id))
            member_ids = [str(member['user_id']) for member in group_members]
            njuit_users = await NjuitStu.filter(push=True, user_id__in=member_ids, dorm_id__isnull=False).all()
            if not njuit_users:
                return None
            
            # 收集群中用户的电费信息
            users_data = []
            interface = get_interface(bot)
            if not interface:
                return None
            for user in njuit_users:
                try:
                    fetch_user = await asyncio.wait_for(interface.get_user(user.user_id), timeout=2.0)
                    if fetch_user is None:
                        continue
                    name = getattr(fetch_user, "name", None)
                    avatar = getattr(fetch_user, "avatar", None)
                    balance_info = await cls._get_electricity_balance(user.dorm_id)
                    users_data.append({
                        'name': name or f'用户{user.user_id}',
                        'avatar': avatar or '',
                        'balance': balance_info['balance'],
                        'value': balance_info['value'],
                        'error': balance_info['error']
                    })
                except Exception as e:
                    logger.warning(f"获取用户 {user.user_id} 信息失败: {e}")
                    continue
            # 按电费余额升序排序，异常项置后
            try:
                users_data.sort(key=lambda u: (u.get('error', False), u.get('value', float('inf'))))
            except Exception:
                pass

            return await cls.generate_electricity_image(users_data) if users_data else None
                
        except Exception as e:
            logger.error(f"获取群组 {group_id} 电费提醒失败: {e}")
            return None

    @classmethod
    async def generate_electricity_image(cls, user_data: list) -> Optional[Path]:
        """生成电费提醒的图片（统一UI渲染）"""
        try:
            # 生成内容区域html
            content_html = "".join(cls._generate_user_html(user) for user in user_data)
            # 使用UI统一渲染
            image_bytes = await ui.render_template(
                "pages/builtin/njuit_guide/electricity_template.html",
                data={"content": content_html},
                viewport={"width": 400, "height": 10},
            )

            # 兼容原有返回文件路径的调用方：写入到固定路径后返回
            save_path = FILE_PATH / "electricity_reminder.jpg"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(image_bytes)
            return save_path
                
        except Exception as e:
            logger.error(f"生成电费图片失败: {e}")
            return None