import uvicorn
from fastapi import FastAPI, APIRouter

from apps.menu.api import menu, submenu, dish
from apps.menu.models import Base
from core.database import engine

app = FastAPI()
router = APIRouter(prefix='/api/v1')

router.include_router(menu.router)
router.include_router(submenu.router)
router.include_router(dish.router)
app.include_router(router)
Base.metadata.create_all(engine)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
