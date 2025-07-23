from fastapi import APIRouter, Request
from src.database import get_cursor
from src.logger import logger
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/")            # корень теперь здесь
async def analyze(request: Request):
    """Главный обработчик корневого пути /"""
    client_ip = (
        request.headers.get("x-real-ip") or
        request.headers.get("x-forwarded-for") or
        request.client.host
    )
    ua = request.headers.get("user-agent", "")
    short_ua = ua.split()[0] if ua else "Unknown"
    is_mobile = request.headers.get("sec-ch-ua-platform") == '"Android"'

    logger.info(
        f"{request.method} {client_ip} mobile={is_mobile} UA={short_ua}"
    )

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
               (addr, name, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_ip, name, request.method, datetime.now(), is_mobile, short_ua)
        )

    return {"message": "ok"}


@router.get("/stats")
async def stats():
    """JSON-эндпоинт для дашборда"""
    with get_cursor() as (cur, _):
        # всего запросов
        cur.execute("SELECT COUNT(*) FROM hikariplus")
        rc = cur.fetchone()[0]

        # уникальные адреса и количество
        cur.execute("SELECT addr, COUNT(*) AS c FROM hikariplus GROUP BY addr")
        uc_rows = cur.fetchall()
        uc = len(uc_rows)
        test = {ip: cnt for ip, cnt in uc_rows}

        # уникальные адреса и количество2
        cur.execute("SELECT DISTINCT(addr), COUNT(*) AS req_count FROM hikariplus GROUP BY addr ORDER BY req_count DESC limit 10")
        uco_rows = cur.fetchall()
        uco = len(uc_rows)
        uniq= {ip: cnt for ip, cnt in uc_rows}

        # мобильные
        cur.execute(
            "SELECT addr FROM hikariplus WHERE is_mobile='True' GROUP BY addr"
        )
        mc_rows = cur.fetchall()
        mc = len(mc_rows)
        mcounter = mc_rows

    return {"rc": rc, "uc": uc, "test": test, "mc": mc, "mcounter": mcounter, "uco": uco, "uniq": uniq}