from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation, TradingHistory


access_logger = logging.getLogger("uvicorn.access")

# 성공 http200 log 안뜨도록 
class IgnoreUserIdsFilter(logging.Filter):
    def filter(self, record):
        return "/api/wallet" not in record.getMessage()

access_logger.addFilter(IgnoreUserIdsFilter())

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WalletRequest(BaseModel):
    timezone: str


@router.post("/wallet")
async def datalist(request: Request, body:WalletRequest, db: Session = Depends(get_db)):
    # 현지 시간
    user_tz = ZoneInfo(body.timezone)

    token = request.cookies.get("jwt") 
    
    try:
        payload = jwt.decode(token, "dev_secret_key_12345", algorithms=["HS256"], leeway=10)
        
        id = payload["sub"]
    except jwt.ExpiredSignatureError:
        return JSONResponse(content={"data" : "Nodata"})
    except jwt.InvalidTokenError:
        return JSONResponse(content={"data" : "Nodata"})

    data = {}

    history_list = db.query(TradingHistory) \
        .filter(TradingHistory.userid == id) \
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

    data = { "static_data" : static_data, "variable_data" : variable_data }
    
    context = JSONResponse(content={"data": data})
    return context