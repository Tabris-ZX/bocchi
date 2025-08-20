# 后藤一里 Bot（Bocchi Bot）

> 一个围绕「小孤独」后藤一里形象打造的多平台聊天机器人。  
> 项目在 **“绪山真寻Bot”** 的源码基础上进行二次开发：将原本的「真寻」人设替换为作者钟爱的「小波奇」，并加入了许多新功能和改造。目标是让 Bot 既有个性化的人设体验，也能作为一个功能全面、易于扩展的机器人平台使用。  

## 项目简介
**Bocchi Bot** 基于 **NoneBot2** 与 **go-cqhttp**，通过 **OneBot v11** 协议与 QQ 等平台交互。支持 **指令交互 + 被动触发** 的混合模式。  

与真寻Bot相比，波奇Bot 的主要变化：  

- 🎸 **人设改造**：将原先的「绪山真寻」替换为「后藤一里」，全局交互文本、人设细节与语气风格全部更新；  
- ✨ **功能拓展**：在真寻Bot的功能基础上，新增了更多插件和特色能力；  
- 🛠 **架构优化**：调整了数据库上下文（`db_context`）、配置目录（`configs`），让结构更清晰；  
- 🖼 **多媒体支持**：增强了图文处理与 HTML 渲染能力，更适合富展示消息；  
- 🔌 **插件兼容**：保留了大部分与真寻Bot 兼容的插件生态，同时提供了新的内置功能。 

整体目标是：让用户能够 **轻松拥有一个带有“小波奇”人设的 Bot**，既能陪伴日常，也能承担各种实用功能。  


## 技术结构
项目目录说明：  
- `bocchi/builtin_plugins` 与 `bocchi/plugins`：内置和扩展功能模块；  
- `bocchi/services/db_context`：数据库连接与初始化逻辑；  
- `bocchi/configs`：运行配置与路径约定。  

## 参考项目
- **绪山真寻Bot（Zhenxun Bot）**  
  - 本项目的基础源码来源  
  - 仓库地址：[zhenxun-org/zhenxun_bot](https://github.com/zhenxun-org/zhenxun_bot.git)  

同时，本项目还参考了 **NoneBot2 生态** 的部分优秀插件与实践，感谢所有开源贡献者 🙏。  

## 作者与联系
- 作者：**Tabris_ZX**  
- 项目地址：[Tabris-ZX/bocchi](https://github.com/Tabris-ZX/bocchi.git)  
- 协议：**AGPL-3.0**（详见仓库内 `LICENSE`）  
- 版本：见仓库根目录 `__version__`  
- 联系方式：3146463122@qq.com / tabris.algo@gmail.com  
