import os
import sys
import time

from app.api.routes import chat
from app.api.routes import settings as settings_router
from app.config import STATIC_DIR, UPLOAD_DIR
from app.core.settings import get_settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

# ロギング設定
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "logs/agent.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG",
)

# 設定の読み込み
app_settings = get_settings()

# FastAPIアプリケーションの作成
app = FastAPI(
    title="AI Agent API",
    description="AIエージェントのREST API",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])

# 静的ファイルの設定
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# リクエスト処理時間測定ミドルウェア
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    # 接続元IPアドレスの取得
    client_host = request.client.host if request.client else "unknown"
    client_query = str(request.query_params) if request.query_params else ""

    # リクエストログ
    logger.info(
        f"リクエスト受信: {request.method} {request.url.path} - 接続元IP: {client_host}, クエリ: {client_query}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # レスポンスログ
    logger.info(
        f"レスポンス送信: {request.method} {request.url.path} - 処理時間: {process_time:.4f}秒, ステータス: {response.status_code}"
    )

    return response


# エラーハンドラ
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"グローバルエラーハンドラ: {str(exc)}")
    return JSONResponse(
        status_code=500, content={"detail": f"内部サーバーエラー: {str(exc)}"}
    )


# ルートエンドポイント
@app.get("/")
async def root():
    return {"name": "AI Agent API", "version": "0.1.0", "status": "running"}


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": time.time()}


# アプリケーション起動時の処理
@app.on_event("startup")
async def startup_event():
    logger.info("アプリケーション起動")

    # アップロードディレクトリの作成
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"アップロードディレクトリを確認: {UPLOAD_DIR}")

    # 設定の読み込み
    logger.info(f"環境: {app_settings.env}")
    logger.info(f"LLMプロバイダー: {app_settings.default_llm_provider}")


# アプリケーション終了時の処理
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("アプリケーション終了")


# 開発サーバー起動用コード
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=app_settings.api_host,
        port=app_settings.api_port,
        reload=app_settings.api_debug,
    )
