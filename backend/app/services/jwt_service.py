from app.common.imports import *

from google.oauth2 import id_token
from google.auth.transport import requests

app = FastAPI()

@app.get("/google-test")
def google_test():
    return {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_OAUTH_USER_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_OAUTH_USER_CLIENT_PASSWORD"),
        "REDIRECT_URI": os.getenv("USER_REDIRECT_URI")
    }

class TokenJwt():
    load_dotenv(r"C:\Users\HONG\Desktop\investMario\.env")

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


    def refresh_token(self):
        try:
            payload = jwt.decode(self.token, self.SECRET_KEY, algorithms=[self.ALGORITHM], options={"verify_exp": False})
            payload["exp"] = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
            new_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
            return new_token
        except Exception as e:
            print("토큰 재발급 실패:", e)
            return None
        