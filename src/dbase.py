import mysql.connector
from mysql.connector import pooling
import yaml
from contextlib import contextmanager
from datetime import datetime, timedelta
from src.logger import logger

# Читаем конфигурацию один раз
with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)

# Пул соединений
pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    user=conf['user'],
    password=conf['password'],
    host=conf['host_db'],
    database=conf['database']
)

DB_CFG = {
    "user":     conf['user'],
    "password": conf['password'],
    "host":     conf['host_db'],
    "database": conf['database'],
    "charset":  "utf8mb4"
}

@contextmanager
def get_cursor():
    conn = pool.get_connection()
    cur = conn.cursor(buffered=True)
    try:
        yield cur, conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@contextmanager
def transaction():
    """Контекстный менеджер для транзакций."""
    conn = pool.get_connection()          # ваш существующий способ получить соединение
    cur = conn.cursor()
    try:
        yield cur, conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.exception("Транзакция отменена: %s", exc)
        raise
    finally:
        cur.close()
        conn.close()

# ---------- вспомогательная функция ----------
def fetch_for_table(tbl: str):
    conn = mysql.connector.connect(**DB_CFG)
    cur = conn.cursor(dictionary=True)
    now = datetime.utcnow()
    start = now - timedelta(days=31)

    def q(sql, params=()):
        cur.execute(sql, params)
        return cur.fetchall()

    # 1. total_hits
    total_hits = int(q(f"SELECT COUNT(*) AS c FROM `{tbl}`")[0]['c'])

    # 2. unique_ips_24h
    unique_ips_24h = int(q(f"""
        SELECT COUNT(DISTINCT addr) AS c 
        FROM `{tbl}` 
        WHERE timed >= NOW() - INTERVAL 24 HOUR and addr !='85.192.130.91'
    """)[0]['c'])
    # 3. recent_rows
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
        FROM `{tbl}` where addr !='85.192.130.91'
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
          SUM(is_mobile=1)/COUNT(*) AS y
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
                WHEN user_agent REGEXP 'Chrome/[0-9]' THEN 'Chrome'
                WHEN user_agent REGEXP 'Firefox/[0-9]' THEN 'Firefox'
                WHEN user_agent REGEXP 'Safari/[0-9]' AND user_agent NOT REGEXP 'Chrome/[0-9]' THEN 'Safari'
                ELSE 'Other'
            END AS label,
            COUNT(*) AS value
        FROM `{tbl}`
        WHERE timed >= %s
        GROUP BY label
    """, (start,))


    # отдаём словарь (всё уже int/float/str)
    return {
        "total_hits": total_hits,
        "unique_ips_24h": unique_ips_24h,
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
