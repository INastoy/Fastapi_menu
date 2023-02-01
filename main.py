import uvicorn
from fastapi import FastAPI, APIRouter

from apps.auth.api import auth
from apps.menu.api import menu, submenu, dish
from core.openapi_tags import tags_metadata

app = FastAPI(title='Restaurant API', openapi_tags=tags_metadata, debug=True)
router = APIRouter(prefix='/api/v1')

router.include_router(menu.router)
router.include_router(submenu.router)
router.include_router(dish.router)
router.include_router(auth.router)
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
