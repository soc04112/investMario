from app.common.imports import *

from app.api.routers import login, send_data, userinfor, userinfo_modify, verfyjwt, logout
from app.database.connection import get_connection
from app.api.config.config import Base, engine
from app.api.routers import agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        print("DB 연결 성공:", cur.fetchone())

        Base.metadata.create_all(bind=engine) ## 이부분 변경됨
        conn.close()
    except Exception as e:
        print("DB 연결 실패:", e)

    yield  #

    print("서버 종료 중...")

app = FastAPI(lifespan=lifespan)

ENV = os.getenv("APP_ENV", "production") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(userinfor.router, prefix="/api")
app.include_router(userinfo_modify.router, prefix="/api")
app.include_router(login.router, prefix="/api")
app.include_router(send_data.router, prefix="/api")
app.include_router(verfyjwt.router, prefix="/api")
app.include_router(logout.router, prefix="/api")
app.include_router(agent.router, prefix="/api")