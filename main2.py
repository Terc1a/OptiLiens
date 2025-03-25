from fastapi import FastAPI, Request
from user_agents import parse
import uvicorn
import logging
from datetime import datetime
import yaml

#Настройки логгера
logger = logging.getLogger(__name__)

app = FastAPI()

# def log_request(request: Request, client_ip: str):
    # """Функция для логирования в терминал"""
    # print("\n" + "=" * 50)
    # print(f"📨 Новый запрос ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    # print(f"🌐 IP: {client_ip}")
    # print(f"🛠️ Метод: {request.method}")
    # print(f"🔗 URL: {request.url}")
    # print(f"🧐 Заголовки:")
    # for name, value in request.headers.items():
        # print(f"  • {name}: {value}")
    # print("=" * 50 + "\n")


@app.get('/')
async def analyze_request(request: Request):
    client_ip = request.headers.get("x-real-ip") or \
                request.headers.get("x-forwarded-for") or \
                request.client.host
    usagent = request.headers.get('user-agent')
    lstring = usagent.split()[0]

    # logger.info(f"\n{'='*50}\n"
                # f"Request: {request.method} {request.url}\n"
                # f"IP: {client_ip}\n"
                # f"Headers: {dict(request.headers)}\n"
                # f"{'='*50}")
    logger.info(f"\n{'='*50}\n"
                f"req_method: {request.method}\n"
                f"user_ip: {client_ip}\n"
                f"platform: {request.headers.get('sec-ch-ua-platform')}\n"
                f"user-agent: {lstring}\n"
                f"timestamp: {datetime.now()}\n"
                f"uname: {client_ip}\n"
                
                f"{'='*50}"
    )
    return {"message":'sosi jopu'}
    


if __name__ == "__main__":
    
    uvicorn.run(app, host="192.168.0.11", port=5556, log_config='log_conf.yaml')

