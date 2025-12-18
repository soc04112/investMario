from app.common.imports import *
from app.services.jwt_service import TokenJwt

router = APIRouter()

@router.post("/verifyjwt")
async def verify_jwt(request: Request):
    token = request.cookies.get("jwt")

    if not token:
        print("오류")
        raise HTTPException(status_code=401, detail="JWT not found")

    jwt_service = TokenJwt(token=token)

    try:
        payload = jwt_service.decode_token()
        return {"message": "verified", "payload": payload}
    except Exception:
        print("오류")        
        raise HTTPException(status_code=401, detail="Invalid JWT")