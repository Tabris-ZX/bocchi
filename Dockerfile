FROM python:3.12-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# --- 关键修改：更换腾讯云软件源并安装依赖 ---
RUN sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*
# ------------------------------------------

# 安装 Poetry (同样使用清华源)
RUN pip install --no-cache-dir poetry -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制配置文件
COPY pyproject.toml poetry.lock* ./

# 安装项目依赖
RUN poetry install --no-root --without dev

# 复制源码
COPY . .

CMD ["python", "bot.py"]