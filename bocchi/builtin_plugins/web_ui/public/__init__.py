from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from bocchi.services.log import logger
from bocchi.utils.manager.bocchi_repo_manager import bocchiRepoManager

router = APIRouter()


@router.get("/")
async def index():
    return FileResponse(bocchiRepoManager.config.WEBUI_PATH / "index.html")


@router.get("/favicon.ico")
async def favicon():
    return FileResponse(bocchiRepoManager.config.WEBUI_PATH / "favicon.ico")


async def init_public(app: FastAPI):
    try:
        if not bocchiRepoManager.check_webui_exists():
            await bocchiRepoManager.webui_update(branch="test")
        folders = [
            x.name for x in bocchiRepoManager.config.WEBUI_PATH.iterdir() if x.is_dir()
        ]
        app.include_router(router)
        for pathname in folders:
            logger.debug(f"挂载文件夹: {pathname}")
            app.mount(
                f"/{pathname}",
                StaticFiles(
                    directory=bocchiRepoManager.config.WEBUI_PATH / pathname,
                    check_dir=True,
                ),
                name=f"public_{pathname}",
            )
    except Exception as e:
        logger.error("初始化 WebUI资源 失败", "WebUI", e=e)
