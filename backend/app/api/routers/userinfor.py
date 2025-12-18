from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation, TradingHistory

router = APIRouter()



fernet_key = os.getenv("FERNET_KEY").encode() 
cipher = Fernet(fernet_key)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_key_valid(enc_dict, key_name, subkeys=None):
    """
    enc_dict: account.key 딕셔너리
    key_name: 'grok', 'open', 'upbit', 'bithumb' 등
    subkeys: None 또는 ['access', 'secret']
    """
    if key_name not in enc_dict:
        return False

    try:
        if subkeys:
            # access + secret 모두 체크
            for subkey in subkeys:
                if subkey not in enc_dict[key_name]:
                    return False
                decrypted = cipher.decrypt(enc_dict[key_name][subkey].encode()).decode()
                if not decrypted.strip():
                    return False
            return True
        else:
            # 단일 secret만 체크
            if 'secret' not in enc_dict[key_name]:
                return False
            decrypted = cipher.decrypt(enc_dict[key_name]['secret'].encode()).decode()
            return bool(decrypted.strip())
    except Exception:
        return False

class WalletRequest(BaseModel):
    timezone: str

def safe_decrypt(value: str) -> str:
    """
    value: 암호화된 문자열
    return: 복호화 문자열, 실패하면 빈 문자열
    """
    if not value:
        return ""
    try:
        return cipher.decrypt(value.encode()).decode()
    except Exception:
        return ""

@router.post("/get_user")
async def user_data(request: Request, body:WalletRequest, db: Session = Depends(get_db)):
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
    
    
    account = db.query(UserInformation) \
        .filter(UserInformation.userid == id).first()

    userinfo = {
        "username": account.userinfo['username'],
        "usemodel": account.userinfo['usemodel'],
        "colors": account.userinfo['colors'],
        "logo": account.userinfo['logo'],
        "post": account.userinfo['post'],
        "email": account.userinfo['email'],
        "country": account.userinfo['country'],
        "createdtime": account.userinfo['createdtime'],
        "phone": account.userinfo['phone'],
        "tier": account.money['tier'],
        "tier_time": account.money['tier_time'],
        "play": account.usercustom['play'],
        "ticker": account.usercustom['ticker'],
        "exchange": account.usercustom['exchange'],
        "interval": account.usercustom['interval'],
        "trading_fee": account.usercustom['trading_fee'],
        "user_prompt": account.usercustom['user_prompt'],
        
        "grok_key": is_key_valid(account.key, 'grok'),
        "gpt_key": is_key_valid(account.key, 'open'),
        "gemini_key": is_key_valid(account.key, 'gemini'),
        "upbit_key": is_key_valid(account.key, 'upbit', subkeys=['access', 'secret']),
        "bithumb_key": is_key_valid(account.key, 'bithumb', subkeys=['access', 'secret']),
        "bingx" : is_key_valid(account.key, "bingx", subkeys=['access', 'secret']),

        "grok_secret_key": safe_decrypt(account.key.get('grok', {}).get('secret', "")),
        "gpt_secret_key": safe_decrypt(account.key.get('open', {}).get('secret', "")),
        "gemini_secret_key": safe_decrypt(account.key.get('gemini', {}).get('secret', "")),
        "upbit_access_key": safe_decrypt(account.key.get('upbit', {}).get('access', "")),
        "upbit_secret_key": safe_decrypt(account.key.get('upbit', {}).get('secret', "")),
        "bithumb_access_key": safe_decrypt(account.key.get('bithumb', {}).get('access', "")),
        "bithumb_secret_key": safe_decrypt(account.key.get('bithumb', {}).get('secret', "")),
        "bingx_access_key" : safe_decrypt(account.key.get('bingx', {}).get('access', "")),
        "bingx_secret_key" : safe_decrypt(account.key.get('bingx', {}).get('secret', "")),
    }

    return userinfo