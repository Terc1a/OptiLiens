import mysql.connector
from mysql.connector import pooling
import yaml
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
import json

with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    user=conf['user'],
    password=conf['password'],
    host=conf['host_db'],
    database=conf['database'],
    charset=conf['charset']
)

@contextmanager
def get_cursor():
    conn = pool.get_connection()
    cur = conn.cursor(buffered=True)      # ← tuple, как было
    try:
        yield cur, conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def json_serial(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat() + 'Z'
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    raise TypeError

# ---------- старая функция без изменений ----------
def fetch_for_table(tbl: str):
    conn = mysql.connector.connect(
        user=conf['user'],
        password=conf['password'],
        host=conf['host_db'],
        database=conf['database'],
        charset=conf['charset']
    )
    cur = conn.cursor()
    now = datetime.utcnow()
    start = now - timedelta(hours=24)

    def q(sql, params=()):
        cur.execute(sql, params)
        return cur.fetchall()

    total_hits = int(q(f"SELECT COUNT(*) AS c FROM `{tbl}`")[0][0])

    recent_rows = q(f"""
        SELECT
          REGEXP_REPLACE(addr,'([0-9]+\\\\.[0-9]+\\\\.)[0-9]+\\\\.[0-9]+','$1xxx.xxx') AS addr,
          name, method, timed, is_mobile,
          CONCAT(LEFT(user_agent,60),'...') AS user_agent
        FROM `{tbl}`
        ORDER BY timed DESC
        LIMIT 20
    """)

    hits = q("""
        SELECT UNIX_TIMESTAMP(timed)*1000 AS x, COUNT(*) AS y
        FROM `{}`
        WHERE timed >= %s
        GROUP BY x
        ORDER BY x
    """.format(tbl), (start,))

    uniq = q("""
        SELECT UNIX_TIMESTAMP(timed)*1000 AS x, COUNT(DISTINCT addr) AS y
        FROM `{}`
        WHERE timed >= %s
        GROUP BY x
        ORDER BY x
    """.format(tbl), (start,))

    mobile = q("""
        SELECT UNIX_TIMESTAMP(timed)*1000 AS x,
               SUM(is_mobile='true')/COUNT(*) AS y
        FROM `{}`
        WHERE timed >= %s
        GROUP BY x
        ORDER BY x
    """.format(tbl), (start,))

    top_methods = q(
        "SELECT method AS label, COUNT(*) AS value "
        f"FROM `{tbl}` WHERE timed >= %s "
        "GROUP BY method ORDER BY value DESC LIMIT 5",
        (start,)
    )

    top_endpoints = q(
        "SELECT name AS label, COUNT(*) AS value "
        f"FROM `{tbl}` WHERE timed >= %s "
        "GROUP BY name ORDER BY value DESC LIMIT 5",
        (start,)
    )

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

def global_unique_ips() -> int:
    conn = mysql.connector.connect(
        user=conf['user'],
        password=conf['password'],
        host=conf['host_db'],
        database=conf['database']
    )
    cur = conn.cursor()
    now = datetime.utcnow()
    start = now - timedelta(hours=24)
    tables = ['blog', 'hikariplus', 'manage', 'todo', 'wishes']

    unions = " UNION ALL ".join(
        f"SELECT addr FROM `{t}` WHERE timed >= %s" for t in tables
    )
    cur.execute(
        f"SELECT COUNT(DISTINCT addr) FROM ({unions}) AS u",
        [start] * len(tables)
    )
    result = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    return result
