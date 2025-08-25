from fastapi import APIRouter, Request
from src.dbase import get_cursor, transaction
from src.logger import logger
import uuid
from datetime import datetime, timedelta
import yaml
import mysql.connector
import json
from decimal import Decimal
from fastapi.responses import JSONResponse
from src.dbase import fetch_for_table, get_services
import httpx
import asyncio

router = APIRouter()

# ---------- конфиг ----------
with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)

DB_CFG = {
    "user":     conf['user'],
    "password": conf['password'],
    "host":     conf['host_db'],
    "database": conf['database'],
    "charset":  "utf8mb4"
}
TABLES = ['blog', 'hikariplus', 'manage', 'todo', 'wishes']

# ---------- универсальный сериализатор ----------
def json_serial(obj):
    """Преобразует Decimal, datetime и прочее в JSON-совместимое"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat() + 'Z'
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    raise TypeError


@router.get("/home/{path:path}")            # mirroring для hikariplus.ru
async def analyze_home(request: Request):
    """Получаем реальный IP клиента из X-Forwarded-For"""
    def get_client_ip(request):
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host

    client_ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "Unknown")
    user_agent = ua if ua else "Unknown"
    is_mobile = "iPhone" in ua or "Android" in ua
    original_path = request.headers.get("x-original-path", str(request.url.path))

    logger.info(f"Real client IP: {client_ip}")

    with get_cursor() as (cur, _):
        # Есть ли такой IP?
        cur.execute(
            "SELECT name FROM hikariplus WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO hikariplus
               (addr, name, direction, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
        )

    return {"message": "ok"}


@router.get("/wishes/{path:path}")            # mirroring для wish.hikariplus.ru
async def analyze_wishes(request: Request):
    """Получаем реальный IP клиента из X-Forwarded-For"""
    def get_client_ip(request):
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host

    client_ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "Unknown")
    user_agent = ua if ua else "Unknown"
    is_mobile = "iPhone" in ua or "Android" in ua
    original_path = request.headers.get("x-original-path", str(request.url.path))

    logger.info(f"Real client IP: {client_ip}")

    with get_cursor() as (cur, _):
        # Есть ли такой IP?
        cur.execute(
            "SELECT name FROM wishes WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO wishes
               (addr, name, direction, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
        )

    return {"message": "ok"}


@router.get("/manage/{path:path}")
async def analyze_manage(request: Request):
    """Получаем реальный IP клиента из X-Forwarded-For"""
    def get_client_ip(request):
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host

    client_ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "Unknown")
    user_agent = ua if ua else "Unknown"
    is_mobile = "iPhone" in ua or "Android" in ua
    original_path = request.headers.get("x-original-path", str(request.url.path))

    logger.info(f"Real client IP: {client_ip}")

    with get_cursor() as (cur, _):
        # Есть ли такой IP?
        cur.execute(
            "SELECT name FROM manage WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO manage
               (addr, name, direction, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
        )

    return {"message": "ok"}


@router.get("/blog/{path:path}")            # mirroring для blog.hikariplus.ru
async def analyze_blog(request: Request):
    """Получаем реальный IP клиента из X-Forwarded-For"""
    def get_client_ip(request):
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host

    client_ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "Unknown")
    user_agent = ua if ua else "Unknown"
    is_mobile = "iPhone" in ua or "Android" in ua
    original_path = request.headers.get("x-original-path", str(request.url.path))

    logger.info(f"Real client IP: {client_ip}")

    with get_cursor() as (cur, _):
        # Есть ли такой IP?
        cur.execute(
            "SELECT name FROM blog WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO blog
               (addr, name, direction, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
        )

    return {"message": "ok"}


@router.get("/todo/{path:path}")            # mirroring для todo.hikariplus.ru
async def analyze_todo(request: Request):
    """Получаем реальный IP клиента из X-Forwarded-For"""
    def get_client_ip(request):
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host

    client_ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "Unknown")
    user_agent = ua if ua else "Unknown"
    is_mobile = "iPhone" in ua or "Android" in ua
    original_path = request.headers.get("x-original-path", str(request.url.path))

    logger.info(f"Real client IP: {client_ip}")

    with get_cursor() as (cur, _):
        # Есть ли такой IP?
        cur.execute(
            "SELECT name FROM todo WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO todo
               (addr, name, direction, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
        )

    return {"message": "ok"}


@router.get("/stats")
async def stats():
    """JSON-эндпоинт для дашборда"""
    with get_cursor() as (cur, _):
        # уникальные адреса и количество
        cur.execute("SELECT COUNT(*) FROM hikariplus")
        home_count = cur.fetchall()
        # уникальные адреса и количество2
        cur.execute("SELECT COUNT(*) FROM wishes")
        wish_count = cur.fetchall()
        # уникальные адреса и количество3
        cur.execute("SELECT COUNT(*) FROM manage")
        manage_count = cur.fetchall()
        # уникальные адреса и количество4
        cur.execute("SELECT COUNT(*) FROM blog")
        blog_count = cur.fetchall()
        # уникальные адреса и количество5
        cur.execute("SELECT COUNT(*) FROM todo")
        todo_count = cur.fetchall()

    return {"home": home_count, "wish": wish_count, "manage": manage_count, "blog": blog_count, "todo": todo_count}


@router.get("/pub_dash")
async def pub_dash():
    print(get_services(), 'get services test')
    now = datetime.utcnow()
    services = {tbl: fetch_for_table(tbl) for tbl in TABLES}
    logger.info(f"Wishes unique_ips_24h: {services['wishes']['unique_ips_24h']}")    # Глобальный подсчет уникальных IP
    conn = mysql.connector.connect(**DB_CFG)
    cur = conn.cursor()

    # Подсчет уникальных IP за 24 часа для всех сервисов
    unions = " UNION ALL ".join(
        f"SELECT addr FROM `{t}` WHERE timed >= %s and addr !='85.192.130.91'" for t in TABLES
    )
    cur.execute(
        f"SELECT COUNT(DISTINCT addr) FROM ({unions}) AS u where addr !='85.192.130.91'",
        [now - timedelta(hours=24)] * len(TABLES)
    )
    global_unique = int(cur.fetchone()[0])
    cur.close()
    conn.close()

    payload = {
        "services": services,
        "global": {
            "last_update": now.isoformat(timespec='seconds') + 'Z',
            "total_hits": sum(s["total_hits"] for s in services.values()),
            "total_unique_ips": global_unique,
            "unique_ips_24h": global_unique  # Дублируем для удобства
        }
    }

    return JSONResponse(content=json.loads(json.dumps(payload, default=json_serial)))


def create_service_router(service_name: str) -> APIRouter:
    """Создаёт роутер для указанного сервиса"""
    router = APIRouter()

    @router.get(f"/{service_name}/{{path:path}}")
    async def analyze_service(request: Request):
        """Получаем реальный IP клиента из X-Forwarded-For"""
        def get_client_ip(request):
            if x_forwarded_for := request.headers.get("x-forwarded-for"):
                return x_forwarded_for.split(",")[0].strip()  # Берём первый IP
            if x_real_ip := request.headers.get("x-real-ip"):
                return x_real_ip
            return request.client.host
        
        client_ip = get_client_ip(request)
        ua = request.headers.get("user-agent", "Unknown")
        user_agent = ua if ua else "Unknown"
        is_mobile = "iPhone" in ua or "Android" in ua
        original_path = request.headers.get("x-original-path", str(request.url.path))

        with transaction() as (cur, _):
            cur.execute(f"SELECT name FROM {service_name} WHERE addr=%s LIMIT 1", (client_ip,))
            row = cur.fetchone()
            name = row[0] if row else str(uuid.uuid4())

            cur.execute(
                f"""INSERT INTO {service_name}
                   (addr, name, direction, method, timed, is_mobile, user_agent)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (client_ip, name, original_path, request.method, datetime.now(), is_mobile, user_agent)
            )

        return {"message": "ok"}
    
    return router


@router.post("/register_service")
async def register_service(service_name: str, service_domain: str):
    # Проверка существования такого сервиса
    try:
        with get_cursor() as (cur, conn):
            cur.execute(f"SELECT s_name FROM services WHERE s_name='{service_name}'")
            if cur.fetchall(): 
                return {"status": "service exist"}
            
            cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_name='{service_name}'")
            if cur.fetchall():
                return {"status": "service exist"}
                
    except Exception as e:
        logger.error(f"Error checking service existence: {e}")
        return {"status": "error", "message": str(e)}
    
    # Создание таблицы сервиса
    try:
        with transaction() as (cur, conn):
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{service_name}` (
                    `addr` varchar(255) DEFAULT NULL,
                    `name` varchar(255) DEFAULT NULL,
                    `method` varchar(255) DEFAULT NULL,
                    `timed` datetime DEFAULT NULL,
                    `is_mobile` varchar(255) DEFAULT NULL,
                    `user_agent` varchar(255) DEFAULT NULL,
                    `direction` varchar(255) DEFAULT '/'
                )
            """)
            # Добавление в registered_services
            cur.execute("""
                INSERT INTO services (s_name, s_domain, reg_date)
                VALUES (%s, %s, %s)
            """, (service_name, service_domain, datetime.now()))
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        return {"status": "error", "message": str(e)}
    
    return {"status": "ok"}


@router.get("/services")
async def get_services():
    with get_cursor() as (cur, _):
        cur.execute("SELECT s_name, s_domain, reg_date FROM services")
        rows = cur.fetchall()
    return {"services": rows}


@router.get("/services_status")
async def services_status():
    statuses = {}
    with get_cursor() as (cur, _):
        # Выбираем только имя и домен
        cur.execute("SELECT s_name, s_domain FROM services")
        services = cur.fetchall()

    async def check_service(name: str, domain: str):
        """Асинхронно проверяет доступность одного сервиса."""
        try:
            # Используем httpx для асинхронных запросов
            async with httpx.AsyncClient(follow_redirects=True) as client:
                # Проверяем базовый URL, таймаут 10 секунд
                response = await client.get(f"https://{domain}", timeout=10)
                # Считаем сервис активным при любом успешном статусе (2xx)
                return name, response.is_success
        except httpx.RequestError:
            # Если произошла любая ошибка сети/DNS, считаем сервис неактивным
            return name, False

    # Создаем задачи для параллельного выполнения
    tasks = [check_service(name, domain) for name, domain in services]
    # Запускаем все проверки одновременно и ждем результатов
    results = await asyncio.gather(*tasks)

    # Собираем результаты в словарь
    for name, is_active in results:
        statuses[name] = is_active

    return {"statuses": statuses}
    

