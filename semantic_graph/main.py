from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import db_engine
from models import Base
from routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_engine.begin() as engine:
        await engine.run_sync(Base.metadata.create_all)
        yield

def main() -> None:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
