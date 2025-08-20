import nonebot

from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

from bocchi.services.db_context import disconnect

# driver.on_startup(init)
driver.on_shutdown(disconnect)

nonebot.load_plugins("bocchi/builtin_plugins")
nonebot.load_plugins("bocchi/plugins")
nonebot.load_plugin("nonebot_plugin_petpet")
nonebot.load_plugin("nonebot_plugin_resolver2")

if __name__ == "__main__":
    nonebot.run()
