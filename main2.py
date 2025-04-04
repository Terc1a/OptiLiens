from fastapi import FastAPI, Request
from user_agents import parse
import uvicorn
import logging
from datetime import datetime
from mysql.connector import connect, Error
import yaml
import uuid
with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)

#Настройки логгера
logger = logging.getLogger(__name__)

app = FastAPI()

cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
cursor = cnx.cursor(buffered=True)
test_conn = """show tables"""
cursor.execute(test_conn)
result = cursor.fetchall()
cnx.close()
if result:
    logger.info(f'DB Connection successful')

#Обработка запросов на / с основного домена
@app.get('/')
async def analyze_request(request: Request):
    client_ip = request.headers.get("x-real-ip") or \
                request.headers.get("x-forwarded-for") or \
                request.client.host
    usagent = request.headers.get('user-agent')
    platform = request.headers.get('sec-ch-ua-platform')
    lstring = usagent.split()[0]

    if platform == '"Android"':
        is_mobile = True #Пока прило доступно только с андроида, пусть оно отдает не модель платформы, а просто статус да или нет
    else:
        is_mobile = False

    #БОЛЬШЕ логов богу логов
    logger.info(f"\n{'='*50}\n"
        f"🛠️  req_method: {request.method}\n"
        f"🌐 user_ip: {client_ip}\n"
        f"🧐 is_mobile: {is_mobile}\n"
        f"📨 user-agent: {lstring}\n"
        f"timestamp: {datetime.now()}\n"
        f"• uname: {client_ip}\n"
        f"{'='*50}")
    cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
    cursor = cnx.cursor(buffered=True)            
    check_addr_exist = f"""select name from hikariplus where addr='{client_ip}' """
    cursor.execute(check_addr_exist)
    check_res = cursor.fetchall()
    cnx.close()
    if check_res: #Если такой адрес уже есть в БД
        for el in check_res:
            name = str(el[0])
            cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
            cursor = cnx.cursor(buffered=True)
            add_data = f"""insert into hikariplus(addr, name, method, timed, is_mobile, user_agent) values('{client_ip}', '{name}', '{request.method}', '{datetime.now()}', '{is_mobile}', '{lstring}')"""
            cursor.execute(add_data)
            cnx.commit()
            cnx.close()
    else:
        cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
        cursor = cnx.cursor(buffered=True)
        add_data = f"""insert into hikariplus(addr, name, method, timed, is_mobile, user_agent) values('{client_ip}', '{str(uuid.uuid4())}', '{request.method}', '{datetime.now()}', '{is_mobile}', '{lstring}')"""
        cursor.execute(add_data)
        cnx.commit()
        cnx.close()
        
 
    #Возвращаем ответ
    if usagent:
        return {"message":'request been handled successfully'}
    else:
        return {"message": 'request throw an error'}
    

if __name__ == "__main__":
    logger.info(f"Server started at {datetime.now()}")
    uvicorn.run(app, host="192.168.0.11", port=5556, log_config='log_conf.yaml')



 
