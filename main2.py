from fastapi import FastAPI, Request
from src.routes import router           
from src.logger import logger
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from src.dbase import get_cursor
from src.routes import router as base_router  
from src.routes import create_service_router  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://manage.hikariplus.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_all(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    took = (datetime.now() - start).total_seconds()
    logger.info(f"{request.method} {request.url} -> {response.status_code} ({took:.3f}s)")
    return response


# --- 1. Функция для получения списка активных сервисов ---
def get_active_services():
    """Возвращает список сервисов, для которых нужно создать роутеры."""
    with get_cursor() as (cur, _):
        cur.execute("SHOW TABLES")  # Получаем все таблицы в БД
        tables = [row[0] for row in cur.fetchall()]
        # Фильтруем только таблицы сервисов (исключаем системные, например, 'users')
        service_tables = [tbl for tbl in tables if tbl not in ["users"]]
        return service_tables

# --- 2. Динамическая регистрация роутеров для всех сервисов ---
for service_name in get_active_services():
    service_router = create_service_router(service_name)  # Создаём роутер
    app.include_router(service_router)  # Регистрируем его в приложении

app.include_router(base_router)


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.5", port=5556)
