from app.common.imports import *
from app.api.config.config import SessionLocal
from app.api.repositories.DBController import DBController

router = APIRouter()

# DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 요청 Body
class WalletRequest(BaseModel):
    data: dict

# 유저 정보 수정 API
@router.post("/userinfo_modify")
async def user_data(request: Request, body: WalletRequest, db: Session = Depends(get_db)):

    token = request.cookies.get("jwt")
    if not token:
        return JSONResponse(content={"data": "No token"}, status_code=401)

    try:
        payload = jwt.decode(token, "dev_secret_key_12345", algorithms=["HS256"], leeway=10)
    except jwt.ExpiredSignatureError:
        return JSONResponse(content={"data": "Token expired"}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse(content={"data": "Invalid token"}, status_code=401)

    if payload:
        controller = DBController(payload=payload, data=body.data)
        controller.user_information_update()
        return JSONResponse(content={"data": "Update success"})
    
    return JSONResponse(content={"data": "No payload"}, status_code=400)
