from pydantic import BaseModel, Extra
from nonebot import get_driver

driver = get_driver()

class NJUIT_Config(BaseModel):
    topic_num: int = 10
    comment_num: int = 10
    xg_headers: dict[str,str]= {
      "Host": "api.zxs-bbs.cn",
      "Connection": "keep-alive",
      "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0ZW5hbnRJZCI6OSwic2Nob29sSUQiOjEwNzU3LCJzY2hvb2wiOiJcdTUzNTdcdTRlYWNcdTVkZTVcdTRlMWFcdTgwNGNcdTRlMWFcdTYyODBcdTY3MmZcdTU5MjdcdTViNjYiLCJ1dWlkIjo5NTQ0ODA2MTAsImlhdCI6MTc1NzU1NTU3MywiZXhwIjoxNzYwMTQ3NTczfQ.YnoP61kMtxnUNr4CCkLFQPer7AWfx1EqzKu0iGmjjA7jhyXxJUtXXbMA4kJwdUFr--X_C8MqsD69w5-Op7GTogppRv2WiOsHRhzTOVUmlUsjdazk55DQSo7cVC8GPvZJeIRQ0gJ_5bMDjDF59Aka87nDWoMxmh19bAlgpaNZfkA",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254101e) XWEB/16389",
      "xweb_xhr": "1",
      "Content-Type": "application/json",
      "Tenant": "9",
      "Accept": "*/*",
      "Sec-Fetch-Site": "cross-site",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Dest": "empty",
      "Referer": "https://servicewechat.com/wx4380f8ff50924d52/41/page-frame.html",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "zh-CN,zh;q=0.9"
    }
    xg_latest_url:str = "https://api.zxs-bbs.cn/api/client/topics?page=1"
    xg_hot_url:str = "https://apiv2.weiwall.cn/api/client/topics/top?school=ngzd"
    xg_comments_url:str = "https://api.zxs-bbs.cn/api/client/comments"
    bill_header:dict[str,str] = {
      "Host": "wxjf.niit.edu.cn",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254061a) XWEB/16133 Flue",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Referer": "http://wxjf.niit.edu.cn/wechat/elec/index",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "zh-CN,zh;q=0.9",
      "Cookie": "__jsluid_h=70d640378595eb5b40f815b03cb6ad92; new_open_id=oqJgU59Lx3SNaWZGCFH0NiOGxo70; union_id=oKTBz58uQrG2IVhXJSoqqsFe8qA4; JSESSIONID=0702EBA434492800028B2E94F4AF98C6; login_token=0c1104e42eb64c9ab76cdb15fcfdfbf2"
    }
    bill_url:str = "http://wxjf.niit.edu.cn/wechat/elec/recharge?"

njuit_config = NJUIT_Config()