直接照搬真寻的ui渲染管理了...

# 🎨 真寻Bot UI主题系统详解

欢迎来到真寻Bot的UI主题系统！本指南将详细介绍 `resources/themes` 目录的结构、主题的覆盖与回退机制，以及如何创建和自定义您自己的UI组件和主题。

## 目录结构

真寻Bot的UI资源都存放在 `resources/themes` 目录下。每个子目录都代表一个独立的主题。

```
resources/
└── themes/
    ├── default/              # 默认主题（必需，作为所有主题的回退）
    │   ├── assets/           # 静态资源 (图片, JS, CSS, 字体等)
    │   │   ├── css/
    │   │   ├── fonts/
    │   │   └── js/
    │   ├── templates/        # Jinja2 模板文件
    │   │   ├── components/   # 可复用的UI组件 (如表格, 卡片)
    │   │   ├── layouts/      # 布局模板 (如网格, 列布局)
    │   │   ├── pages/        # 完整的页面模板 (如帮助, 商店)
    │   │   └── partials/     # 可被包含的模板片段 (如页眉, 页脚)
    │   └── palette.json      # 主题调色板和设计变量
```

-   **`default/`**: 这是核心主题，也是所有其他主题的基石。**请勿删除或重命名此目录**。当其他主题缺少某个文件时，系统会自动从 `default` 主题中寻找。
-   **`dark/` (或其他自定义主题)**: 您的自定义主题。您可以创建任意多个主题目录。
-   **`assets/`**: 存放静态文件。建议按类型分子目录（如`css`, `fonts`, `js`, `image`）。
-   **`templates/`**: 存放所有 `.html` 或 `.css.jinja` 模板文件。
    -   **`components/`**: 独立的、可复用的UI组件，如一个按钮、一个表格。
    -   **`pages/`**: 完整的、独立的页面，通常由多个组件组合而成，如“帮助页面”。
    -   **`layouts/`**: 用于组合多张图片的布局模板。
    -   **`partials/`**: 模板的“零件”，如 `_base.html`，用于被其他模板继承或包含。
-   **`palette.json`**: 定义主题的核心设计变量，如颜色、字体大小等。这是实现快速主题定制的关键。

## 主题工作机制

### 1. 主题切换

您可以在 `data/config.yaml` 文件中通过修改 `UI` 配置组下的 `THEME` 键来切换全局主题。

```yaml
UI:
  THEME: default  # 将 'default' 修改为您想使用的主题目录名，例如 'dark'
```

修改并保存后，机器人渲染的所有图片都将采用新主题的风格。

### 2. 覆盖与回退机制

这是主题系统最强大的特性。当渲染服务需要一个文件（例如 `pages/builtin/help/main.html`）时，它会按以下顺序查找：

1.  **当前主题目录**: `resources/themes/your_theme/templates/pages/builtin/help/main.html`
2.  **默认主题目录**: `resources/themes/default/templates/pages/builtin/help/main.html`

这意味着：

-   **您无需复制整个 `default` 主题**。只需在您的主题目录中创建您想要修改的文件即可。
-   如果您的主题中没有某个文件，系统会自动使用 `default` 主题中的版本，确保功能不会中断。
-   这使得主题更新和维护变得非常简单。

### 3. `palette.json` 与 CSS 变量

`palette.json` 文件定义了主题的核心设计语言。这些值会被注入到一个名为 `theme.css.jinja` 的基础样式表中，并转换为CSS变量。

**`palette.json` 示例:**
```json
{
  "colors": {
    "primary": "#f67186",
    "background_main": "#ffffff",
    "text_dark": "#333333"
  }
}
```

**在 CSS 中使用:**
```css
.my-component {
  color: var(--color-text-dark);
  background-color: var(--color-background-main);
  border: 1px solid var(--color-primary);
}
```

通过这种方式，您可以仅仅通过修改 `palette.json` 中的颜色值，就改变所有使用这些CSS变量的组件的外观，实现一键换肤。

## 如何自定义

### 方案A：快速修改现有主题（推荐初学者）

1.  **选择一个基础主题**: 决定您是想在 `default` (亮色) 还是 `dark` (暗色) 的基础上修改。
2.  **修改调色板**: 打开对应主题的 `palette.json` 文件，尝试修改里面的颜色值。这是最快看到效果的方式。
3.  **替换静态资源**: 在 `assets` 目录中，用您自己的图片、字体等替换同名文件。
4.  **微调CSS**: 如果您想对某个特定组件进行微调，找到它对应的CSS文件（例如 `templates/components/core/table/main.css`），并修改其中的样式。

### 方案B：创建属于您自己的全新主题（推荐高级用户）

1.  **创建新主题目录**: 在 `resources/themes/` 下创建一个新的文件夹，例如 `my_cool_theme`。
2.  **创建 `palette.json`**: 从 `default` 主题复制 `palette.json` 到您的新主题目录，并根据您的设计修改其中的值。
3.  **按需覆盖模板**:
    -   如果您想完全重写“帮助页面”的布局，就在 `my_cool_theme/templates/pages/core/plugin_help_page/` 目录下创建一个 `main.html` 和 `main.css` 文件。
    -   如果您只想修改“表格组件”的边框颜色，就在 `my_cool_theme/templates/components/core/table/` 目录下创建一个 `main.css` 文件，并只写您想覆盖的样式。
4.  **添加自定义资源**: 将您的字体、背景图片等放入 `my_cool_theme/assets/` 目录。
5.  **激活主题**: 在 `data/config.yaml` 中设置 `THEME: my_cool_theme`。