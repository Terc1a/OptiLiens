from fastapi import APIRouter, Request
from src.database import get_cursor
from src.logger import logger
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/home/")            # mirroring для hikariplus.ru
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


@router.get("/wishes/")            # mirroring для wish.hikariplus.ru
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
            "SELECT name FROM wishes WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO wishes
               (addr, name, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_ip, name, request.method, datetime.now(), is_mobile, short_ua)
        )

    return {"message": "ok"}


@router.get("/manage/")            # mirroring для manage.hikariplus.ru
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
            "SELECT name FROM manage WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO manage
               (addr, name, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_ip, name, request.method, datetime.now(), is_mobile, short_ua)
        )

    return {"message": "ok"}


@router.get("/blog/")            # mirroring для blog.hikariplus.ru
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
            "SELECT name FROM blog WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO blog
               (addr, name, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_ip, name, request.method, datetime.now(), is_mobile, short_ua)
        )

    return {"message": "ok"}


@router.get("/todo/")            # mirroring для todo.hikariplus.ru
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
            "SELECT name FROM todo WHERE addr=%s LIMIT 1",
            (client_ip,)
        )
        row = cur.fetchone()
        name = row[0] if row else str(uuid.uuid4())

        # Записываем визит
        cur.execute(
            """INSERT INTO todo
               (addr, name, method, timed, is_mobile, user_agent)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_ip, name, request.method, datetime.now(), is_mobile, short_ua)
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
