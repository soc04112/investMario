from app.common.imports import *
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests as lib_requests
import urllib3
from datetime import datetime, timedelta, timezone

# SSL 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TokenJwt():
    # .env 로드 (보통 클래스 밖이나 __init__에 두는 것이 좋으나 기존 구조 유지)
    load_dotenv(r".env")

    def __init__(self, authorize_code=None, token=None):
        self.authorize_code = authorize_code
        self.SECRET_KEY = "dev_secret_key_12345"
        self.ALGORITHM = "HS256"
        self.token = token
        
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        self.URI = os.getenv("REDIRECT_URI")
        
    async def authorize_token(self):
        data_set={
            "client_id": self.GOOGLE_CLIENT_ID,
            "client_secret": self.GOOGLE_CLIENT_SECRET,
            "code": self.authorize_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.URI,
            "scope": "openid email profile"
        }
      
        # SSL 검증 우회 (verify=False)
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.post(
                "https://oauth2.googleapis.com/token",
                data=data_set
            )
     
            token_json = res.json()
            if token_json:
                print("authorize_token completed")
            return token_json.get("id_token")

    def verify_google(self, id_token_str):
        try:
            # SSL 검증 우회 세션 설정
            session = lib_requests.Session()
            session.verify = False 
            custom_request = google_requests.Request(session=session)

            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                custom_request,
                self.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60 
            )
            return idinfo 
        except Exception as e:
            print(f"Google ID Token 검증 실패: {e}")
            return None

    def decode_token(self):
        return jwt.decode(self.token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
    # ★ 이 함수의 들여쓰기가 클래스(TokenJwt) 안으로 들어와 있어야 합니다.
    async def generation(self):
        id_token_str = await self.authorize_token()
        if not id_token_str:
            raise ValueError("Google로부터 ID 토큰을 가져오지 못했습니다.")

        google_info = self.verify_google(id_token_str)
        if google_info is None:
            raise ValueError("Invalid Google Access Token")
        
        payload = {
            "sub": google_info["sub"],        
            "email": google_info.get("email"), 
            "name": google_info.get("name"), 
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }

        # payload와 인코딩된 토큰 반환
        return payload, jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def refresh_token(self):
        try:
            payload = jwt.decode(self.token, self.SECRET_KEY, algorithms=[self.ALGORITHM], options={"verify_exp": False})
            payload["exp"] = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
            new_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
            return new_token
        except Exception as e:
            print("토큰 재발급 실패:", e)
            return None