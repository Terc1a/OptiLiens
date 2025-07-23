import mysql.connector
from mysql.connector import pooling
import yaml

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

# Удобный контекстный менеджер
from contextlib import contextmanager

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