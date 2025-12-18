from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation
from app.services.jwt_service import TokenJwt

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

class Token(BaseModel):
    token: str

@router.post("/GoogleLogin")
async def google_login(token_data: Token, response: Response, db: Session = Depends(get_db)):
    authorize_code = token_data.token 

    jwt_service = TokenJwt(authorize_code=authorize_code)

    try:
        payload, jwt_token = await jwt_service.generation()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Access Token")
    except ExpiredSignatureError:
        print("1")
        raise HTTPException(status_code=401, detail="Google Access Token has expired")
    
    response.set_cookie(
        key="jwt",
        value=jwt_token,
        httponly=True,
        secure=False,    
        samesite="lax",   
        max_age=3600     
    )

    # user = db.query(UserInformation).filter_by(userid=payload['sub']).first()

    return {"message": "exists", "userid": payload['sub']}
    # if user:
    #     return {"message": "exists", "userid": payload['sub']}
    # else:
    #     return {"message": "new", "userid": payload['sub']}