import mysql.connector
from mysql.connector import pooling
import yaml
from contextlib import contextmanager
from datetime import datetime, timedelta


DB_CFG = {
    "user":     'analytics',
    "password": 'Zksj-dhfsee87',
    "host":     '192.168.0.100',
    "database": 'analytics',
    "charset":  "utf8mb4"
}

def get_services():
    conn = mysql.connector.connect(**DB_CFG)
    cur = conn.cursor(dictionary=True)
    def q(sql, params=()):
        cur.execute(sql, params)
        return cur.fetchall()
    services = q("SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'analytics' AND table_name NOT IN ('users', 'services')")  
    return [row['TABLE_NAME'] for row in services]

some = get_services()
print(some)
