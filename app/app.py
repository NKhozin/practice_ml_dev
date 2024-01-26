from fastapi import FastAPI
import uvicorn
from routers.ml import ml
from routers.user import user_router


server = FastAPI()


@server.get("/status", tags=["functionality check"])
def get_status():
    """Проверка работы сервиса"""
    return {"status": "Работаем"}


server.include_router(ml, prefix="/ml")
server.include_router(user_router, prefix="/user")


if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000)
