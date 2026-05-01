from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
from config import config
from routers import chat, scenario

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Lexio Backend",
    version="1.0.0",
    description="Lexio AI Legal Assistant Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(scenario.router, prefix="/api", tags=["scenario"])

@app.get("/")
async def root():
    return {"app": "Lexio Backend", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
