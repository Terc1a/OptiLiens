from fastapi import APIRouter, Request
from src.database import get_cursor
from src.logger import logger
import uuid
from datetime import datetime, timedelta
import yaml
import mysql.connector
import json
from decimal import Decimal
from fastapi.responses import JSONResponse

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

# ---------- вспомогательная функция ----------
def fetch_for_table(tbl: str):
    conn = mysql.connector.connect(**DB_CFG)
    cur  = conn.cursor(dictionary=True)
    now  = datetime.utcnow()
    start = now - timedelta(days=31)

    def q(sql, params=()):
        cur.execute(sql, params)
        return cur.fetchall()

    # 1. total_hits
    total_hits = int(q(f"SELECT COUNT(*) AS c FROM `{tbl}`")[0]['c'])

    # 2. recent_rows
# В функции fetch_for_table() замените запрос recent_rows на:
    recent_rows = q(f"""
        SELECT
            CONCAT(
                SUBSTRING_INDEX(addr, '.', 1), '.',
                SUBSTRING_INDEX(SUBSTRING_INDEX(addr, '.', 2), '.', -1), '.',
                SUBSTRING_INDEX(SUBSTRING_INDEX(addr, '.', 3), '.', -1),
                '.xxx'
            ) AS addr,
            direction AS name,
            method, timed, is_mobile,
            CONCAT(LEFT(user_agent, 60), '...') AS user_agent
        FROM `{tbl}`
        ORDER BY timed DESC
        LIMIT 20
    """)


    # 3. hits_series
    hits = q(f"""
        SELECT
          UNIX_TIMESTAMP(DATE(timed))*1000 AS x,
          COUNT(*) AS y
        FROM `{tbl}`
        WHERE timed >= %s
        GROUP BY DATE(timed)
        ORDER BY x
    """, (start,))

    # 4. unique_addr_series
    uniq = q(f"""
        SELECT
            FLOOR(UNIX_TIMESTAMP(timed)/3600)*3600*1000 AS x,
            COUNT(DISTINCT addr) AS y
        FROM `{tbl}`
        WHERE timed >= NOW() - INTERVAL 1 DAY
        GROUP BY x/3600000
        ORDER BY x
    """)

    # 5. mobile_share_series
    mobile = q(f"""
        SELECT
          UNIX_TIMESTAMP(DATE(timed))*1000 AS x,
          SUM(is_mobile='true')/COUNT(*) AS y
        FROM `{tbl}`
        WHERE timed >= %s
        GROUP BY DATE(timed)
        ORDER BY x
    """, (start,))

    # 6. top_methods
    top_methods = q(
        "SELECT direction AS label, COUNT(*) AS value "
        f"FROM `{tbl}` WHERE timed >= %s "
        "GROUP BY direction ORDER BY value DESC LIMIT 5",
        (start,)
    )

    # 7. top_endpoints
    top_endpoints = q(
        "SELECT direction AS label, COUNT(*) AS value "
        f"FROM `{tbl}` WHERE timed >= %s "
        "GROUP BY direction ORDER BY value DESC LIMIT 5",
        (start,)
    )

    # 8. ua_breakdown
    ua = q(f"""
        SELECT
          CASE
            WHEN user_agent LIKE '%%Chrome%%' THEN 'Chrome'
            WHEN user_agent LIKE '%%Firefox%%' THEN 'Firefox'
            WHEN user_agent LIKE '%%Safari%%' THEN 'Safari'
            ELSE 'Other'
          END AS label,
          COUNT(*) AS value
        FROM `{tbl}`
        WHERE timed >= %s
        GROUP BY label
    """, (start,))

    cur.close()
    conn.close()

    # отдаём словарь (всё уже int/float/str)
    return {
        "total_hits": total_hits,
        "recent_rows": recent_rows,
        "hits_series": hits,
        "unique_addr_series": uniq,
        "mobile_share_series": mobile,
        "top_methods": top_methods,
        "top_endpoints": top_endpoints,
        "ua_breakdown": ua,
        "censored_ips": [],
        "censored_ua": []
    }

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
    short_ua = ua.split()[0] if ua else "Unknown"
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
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, short_ua)
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
    short_ua = ua.split()[0] if ua else "Unknown"
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
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, short_ua)
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
    short_ua = ua.split()[0] if ua else "Unknown"
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
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, short_ua)
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
    short_ua = ua.split()[0] if ua else "Unknown"
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
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, short_ua)
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
    short_ua = ua.split()[0] if ua else "Unknown"
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
            (client_ip, name, original_path, request.method, datetime.now(), is_mobile, short_ua)
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


        # уникальные адреса и количество3
        cur.execute("SELECT COUNT(*) FROM blog")
        blog_count = cur.fetchall()


        # уникальные адреса и количество3
        cur.execute("SELECT COUNT(*) FROM todo")
        todo_count = cur.fetchall()

    return {"home": home_count, "wish": wish_count, "manage": manage_count, "blog": blog_count, "todo": todo_count}


@router.get("/pub_dash")
async def pub_dash():
    now = datetime.utcnow()
    services = {tbl: fetch_for_table(tbl) for tbl in TABLES}

    # глобальный unique_ips
    conn = mysql.connector.connect(**DB_CFG)
    cur = conn.cursor()
    unions = " UNION ALL ".join(
        f"SELECT addr FROM `{t}` WHERE timed >= %s" for t in TABLES
    )
    cur.execute(
        f"SELECT COUNT(DISTINCT addr) FROM ({unions}) AS u",
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
            "total_unique_ips": global_unique
        }
    }

    # сериализуем Decimal/datetime и т.д.
    return JSONResponse(content=json.loads(json.dumps(payload, default=json_serial)))
