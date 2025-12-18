from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation, TradingHistory

load_dotenv(r"C:\Users\HONG\Desktop\investMario\.env")

fernet_key = os.getenv("FERNET_KEY").encode() 
cipher = Fernet(fernet_key)

class DBController():
    def __init__(self, payload, data):
        self.userid = payload['sub']
        self.username = payload['name']
        self.email = payload['email']

        self.data = data

    def user_sign(self):
        db = SessionLocal()
        try:
            new_user = UserInformation(
                userid = self.userid,
                userinfo = {
                    "username" : self.username,
                    "usemodel" : "",
                    "colors" : "",
                    "logo" : "",
                    "phone" :"",
                    "email" : self.email,
                    "post" : "",
                    "country" : "",
                    "createdtime": datetime.utcnow().isoformat()
                },

                usercustom = {
                    "prompt_style" : "",
                    "interval" : 0,
                    "play" : "",
                    "user_prompt" : "",
                    "ticker" : {
                        "BTC" : False, 
                        "ETH" : False, 
                        "BCH" : False,
                        "SOL" : False,
                        "XRP" : False
                        },
                    "trading_fee" : "",
                    "exchange" : ""
                },
            
                money = {
                    "tier" : "Demo",
                    "tier_time" : "",                    
                },

                key = {
                    "upbit" : {
                        "access" : "",
                        "secret" : ""
                    },
                    "bithumb" : {
                        "access" : "",
                        "secret" : ""                     
                    },
                    "bingx" :{
                        "access" : "",
                        "secret" : ""        
                    },
                    "open" : {
                        "secret" : ""
                    },
                    "gemini" : {
                        "secret" : ""
                    },
                    "grok" : {
                        "secret" : ""
                    },
                    "claude" : {
                        "secret" : ""
                    }
                },         
            )

            db.add(new_user)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("무결성 오류 발생")            
        except Exception as e:
            db.rollback()
            print(f"오류 발생: {e}")
        finally:
            db.close()

    def user_information_update(self):
        db = SessionLocal()
        update_data = self.data

        try:
            user = db.query(UserInformation).filter_by(userid=self.userid).first()
            if user:
                # 키 암호화
                upbit_access_token = cipher.encrypt(update_data['upbit_access_key'].encode()).decode()
                upbit_secret_token = cipher.encrypt(update_data['upbit_secret_key'].encode()).decode()
                bithumb_access_token = cipher.encrypt(update_data['bithumb_access_key'].encode()).decode()
                bithumb_secret_token = cipher.encrypt(update_data['bithumb_secret_key'].encode()).decode()
                geminiapi = cipher.encrypt(update_data['gemini_key_value'].encode()).decode()
                grokapi = cipher.encrypt(update_data.get('grok_key_value', '').encode()).decode()
                gptapi = cipher.encrypt(update_data.get('gpt_key_value', '').encode()).decode()
                bingx_access_token = cipher.encrypt(update_data['bingx_access_key'].encode()).decode()
                bingx_secret_token = cipher.encrypt(update_data['bingx_secret_key'].encode()).decode()
                # OpenAI / Claude는 필요시 추가
                openapi = ""  
                claudeapi = ""

                # userinfo 업데이트
                user.userinfo = {
                    "username": self.username,
                    "usemodel": update_data['usemodel'],
                    "colors": update_data['colors'],
                    "logo": update_data['logo'],
                    "phone": update_data['phone'],
                    "email": update_data['email'],
                    "post": update_data['post'],
                    "country": update_data.get('country', ''),
                    "createdtime": datetime.utcnow().isoformat()
                }

                # usercustom 업데이트
                user.usercustom = {
                    "prompt_style": "",
                    "interval": update_data['interval'],
                    "play": update_data['play'],
                    "user_prompt": update_data.get('user_prompt', ""),
                    "ticker": update_data['Ticker'],
                    "trading_fee": update_data['trading_fee'],
                    "exchange": update_data['exchange']
                }

                # money 업데이트 (기존 유지)
                user.money = {
                    "tier": update_data.get('tier', 'Demo'),
                    "tier_time": update_data.get('tier_time', "")
                }

                # key 업데이트
                user.key = {
                    "upbit": {"access": upbit_access_token, "secret": upbit_secret_token},
                    "bithumb": {"access": bithumb_access_token, "secret": bithumb_secret_token},
                    "bingx" : {"access": bingx_access_token, "secret": bingx_secret_token},
                    "open": {"secret": openapi},
                    "gemini": {"secret": geminiapi},
                    "grok": {"secret": grokapi},
                    "claude": {"secret": claudeapi},
                    "gpt": {"secret": gptapi}
                }

            db.commit()
            return {"status": "success"}

        except IntegrityError:
            db.rollback()
            print("무결성 오류 발생")
            return {"status": "fail", "error": "IntegrityError"}

        except Exception as e:
            db.rollback()
            print(f"오류 발생: {e}")
            return {"status": "fail", "error": str(e)}

        finally:
            db.close()

    def user_delete(self):
        db = SessionLocal()
        try:
            # UserInformation 삭제
            user = db.query(UserInformation).filter_by(userid=self.userid).first()
            if user:
                db.delete(user)
                db.commit()
            else:
                print("삭제할 유저(UserInformation)가 없습니다.")

            # TradingHistory 삭제
            histories = db.query(TradingHistory).filter_by(userid=self.userid).all()
            if histories:
                for h in histories:
                    db.delete(h)
                db.commit()
            else:
                print("삭제할 유저(TradingHistory)가 없습니다.")

        except IntegrityError:
            db.rollback()
            print("무결성 오류 발생")
        except Exception as e:
            db.rollback()
            print(f"오류 발생: {e}")
        finally:
            db.close()