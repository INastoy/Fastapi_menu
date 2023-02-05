import uvicorn
from celery import Celery
from fastapi import APIRouter, FastAPI

from apps.auth.api import auth
from apps.menu.api import dish, menu, submenu
from core.openapi_tags import tags_metadata
from core.settings import CELERY_BROKER_URL

app = Celery('tasks', broker=CELERY_BROKER_URL, include=['apps.menu.tasks'])
app.conf.accept_content = ['application/json',
                           'application/x-python-serialize']


fastapi_app = FastAPI(
    title='Restaurant API',
    openapi_tags=tags_metadata,
)

router = APIRouter(prefix='/api/v1')

router.include_router(menu.router)
router.include_router(submenu.router)
router.include_router(dish.router)
router.include_router(auth.router)
fastapi_app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('main:fastapi_app', reload=True)
