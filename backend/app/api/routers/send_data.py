from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation, TradingHistory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WalletRequest(BaseModel):
    latest_time: str
    timezone: str


@router.post("/wallet")
async def datalist(request: Request, body:WalletRequest, db: Session = Depends(get_db)):
    if body.latest_time == "0":
        time_dt = datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC"))
    else:
        # latest_time (string) -> timezone-aware local time 
        naive_local_dt = datetime.fromisoformat(body.latest_time)

        # local timezone 객체
        user_tz = ZoneInfo(body.timezone)

        # 로컬 → UTC 변환
        local_dt = naive_local_dt.replace(tzinfo=user_tz)
        time_dt = local_dt.astimezone(ZoneInfo("UTC"))

    # 현지 시간
    user_tz = ZoneInfo(body.timezone)

    mapping_id = {
        "a92f7c1d84b2156e" : "GPT",
        "112345829025586029400" : "GEMINI",
        "d7e41f9ab3659021" : "GROK"
    }

    # 기본 모델
    ids = ["a92f7c1d84b2156e",
           "112345829025586029400",
           "d7e41f9ab3659021"]

    data = {}

    for id in ids:
        history_list = db.query(TradingHistory) \
            .filter(TradingHistory.userid == id) \
            .filter(func.date_trunc('minute', TradingHistory.time) > time_dt) \
            .order_by(TradingHistory.time.asc()) \
            .all()
        
        account = db.query(UserInformation) \
            .filter(UserInformation.userid == id).first()

        key = account.userid

        static_data = {
            "username": account.userinfo['username'],
            "usemodel": account.userinfo['usemodel'],
            "colors": account.userinfo['colors'],
            "logo": account.userinfo['logo'],
        }

        variable_data = []
        # 정리
        for history in history_list:
            utc_history_time = history.time.replace(tzinfo=ZoneInfo("UTC"))

            local_history_time = utc_history_time.astimezone(user_tz)
            time_for_save = local_history_time.replace(second=0, microsecond=0)

            variable_data.append({
                    # 계좌 histroy
                    "time": time_for_save.isoformat(),
                    "position" : history.position,
                    "why" : history.why,
                    "owner_coin" : history.owner_coin,
                    "available_cash": int(history.available),
                    "total_asset": int(history.total_asset),
                })

        data[mapping_id[key]] = { "static_data" : static_data, "variable_data" : variable_data }
    
    # 최신 데이터 시간 구하기
    latest_time = {}
    for key, val in data.items():
        if len(val["variable_data"]) > 0:
            latest_data = val["variable_data"][-1]
            latest_time[key] = latest_data["time"] 

    if len(latest_time) > 0:
        send_latest_time = max(latest_time.values())
    else :
        send_latest_time = body.latest_time
    
    if send_latest_time != body.latest_time:
        context = JSONResponse(content={"data": data, "time": send_latest_time})
        print(f"Payload size: {len(context.body)} bytes")
        return context
    else:
        context = JSONResponse(content={"data" : "Nodata", "time" : "null"})
        print(f"Payload size: {len(context.body)} bytes")
        return context