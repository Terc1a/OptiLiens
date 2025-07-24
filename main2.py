from fastapi import FastAPI, Request
from src.routes import router           # router уже содержит "/" и "/stats"
from src.logger import logger
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # или ["http://192.168.0.4:5000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_all(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    took = (datetime.now() - start).total_seconds()
    logger.info(f"{request.method} {request.url} -> {response.status_code} ({took:.3f}s)")
    return response

# ОДНА строчка — router отдаёт и "/" и "/stats"
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.5", port=5556)
