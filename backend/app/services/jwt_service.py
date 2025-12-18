from app.common.imports import *

from google.oauth2 import id_token
from google.auth.transport import requests

from urllib.parse import quote

app = FastAPI()

@app.get("/google-test")
def google_test():
    return {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_OAUTH_USER_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_OAUTH_USER_CLIENT_PASSWORD"),
        "REDIRECT_URI": os.getenv("USER_REDIRECT_URI")
    }

class TokenJwt():
    load_dotenv(r"C:\python\investMario\.env")

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
      
        async with httpx.AsyncClient() as client:
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
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                self.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60 
            )
            
            return idinfo 
        except ValueError as e:
            print("Google ID Token 검증 실패")
            print("reason : ", e)
            return None
        
    def decode_token(self):
        return jwt.decode(self.token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        
    def get_user_id(self):
        """
        인스턴스에 설정된 self.token으로부터 사용자 ID를 반환합니다.
        우선순위: 'sub' -> 'user_id' -> 'email'
        만료되었거나 디코드 실패 시 None 반환.
        """
        if not self.token:
            print("No token set on TokenJwt instance.")
            return None
        try:
            payload = self.decode_token()
            return payload.get("sub") or payload.get("user_id") or payload.get("email")
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except Exception as e:
            print("Failed to decode token:", e)
            return None

    @classmethod
    def extract_user_id_from_token(cls, token_str, secret_key=None, algorithm=None):
        """
        주어진 JWT 문자열로부터 사용자 ID를 추출하는 유틸리티 메서드(인스턴스 없이 사용 가능).
        secret_key/algorithm을 지정하지 않으면 기본값을 사용합니다.
        실패 시 None 반환.
        """
        secret = secret_key or "dev_secret_key_12345"
        algo = algorithm or "HS256"
        if not token_str:
            return None
        try:
            payload = jwt.decode(token_str, secret, algorithms=[algo])
            return payload.get("sub") or payload.get("user_id") or payload.get("email")
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except Exception as e:
            print("Failed to decode token:", e)
            return None
           
    async def generation(self):
        id_token_str = await self.authorize_token()
        google_info = self.verify_google(id_token_str)
        if google_info is None:
            raise ValueError("Invalid Google Access Token")
        
        payload = {
            "sub": google_info["sub"],        
            "email": google_info.get("email"), 
            "name": google_info.get("name"), 
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }

        return payload, jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
