from app.common.imports import *

from app.api.config.config import SessionLocal, UserInformation, TradingHistory



fernet_key = os.getenv("FERNET_KEY").encode() 
cipher = Fernet(fernet_key)

class DBController():
    def __init__(self, payload, data=None):
        self.userid = payload['sub']
        self.username = payload['name']
        self.email = payload['email']

        self.data = data

    def user_sign_userinformation(self):
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
                    "bingx" : {
                        "access" : "",
                        "secret" : ""                     
                    },                    
                    "gpt" : {
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

    def insert_default_trade(self):
        db = SessionLocal()
        try:
            trade = TradingHistory(
                userid = self.userid,
                trade_number = 0,
                time = datetime.utcnow().isoformat(),
                position = {},
                why = {},
                owner_coin = {},
                average = {},
                trade = {},
                total_asset = 0,
                available = 0
            )

            db.add(trade)
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
        update_data = self.data  # {'user_prompt': '새 프롬프트'} 처럼 일부만 올 수도 있음

        try:
            user = db.query(UserInformation).filter_by(userid=self.userid).first()
            if not user:
                return {"status": "fail", "error": "User not found"}

            # --- 기존 데이터 가져오기 ---
            existing_userinfo = user.userinfo or {}
            existing_usercustom = user.usercustom or {}
            existing_money = user.money or {}
            existing_key = user.key or {}

            # --- 키 암호화 함수 ---
            def encrypt_key(new_value, existing_value):
                return cipher.encrypt(new_value.encode()).decode() if new_value else existing_value or ""

            # --- 키 업데이트 (값이 있을 때만 덮어쓰기) ---
            user.key = {
                "upbit": {
                    "access": encrypt_key(update_data.get('upbit_access_key'), existing_key.get('upbit', {}).get('access')),
                    "secret": encrypt_key(update_data.get('upbit_secret_key'), existing_key.get('upbit', {}).get('secret'))
                },
                "bithumb": {
                    "access": encrypt_key(update_data.get('bithumb_access_key'), existing_key.get('bithumb', {}).get('access')),
                    "secret": encrypt_key(update_data.get('bithumb_secret_key'), existing_key.get('bithumb', {}).get('secret'))
                },
                "bingx" : {
                    "access": encrypt_key(update_data.get('bingx_access_key'), existing_key.get('bingx', {}).get('access')),
                    "secret": encrypt_key(update_data.get('bingx_secret_key'), existing_key.get('bingx', {}).get('secret'))
                },
                "gemini": {"secret": encrypt_key(update_data.get('gemini_key_value'), existing_key.get('gemini', {}).get('secret'))},
                "grok": {"secret": encrypt_key(update_data.get('grok_key_value'), existing_key.get('grok', {}).get('secret'))},
                "claude": {"secret": existing_key.get('claude', {}).get('secret', '')},
                "gpt": {"secret": encrypt_key(update_data.get('gpt_key_value'), existing_key.get('gpt', {}).get('secret'))}
            }

            # --- userinfo 업데이트 ---
            info_keys = ['usemodel', 'colors', 'logo', 'phone', 'email', 'post', 'country']
            user.userinfo = {**existing_userinfo, **{k: update_data[k] for k in info_keys if k in update_data}}
            # username과 생성시간은 항상 갱신
            user.userinfo["username"] = self.username
            user.userinfo["createdtime"] = datetime.utcnow().isoformat()

            # --- usercustom 업데이트 ---
            custom_keys = ['interval', 'play', 'user_prompt', 'ticker', 'trading_fee', 'exchange']
            user.usercustom = {**existing_usercustom, **{k: update_data[k] for k in custom_keys if k in update_data}}

            # --- money 업데이트 ---
            money_keys = ['tier', 'tier_time']
            user.money = {**existing_money, **{k: update_data[k] for k in money_keys if k in update_data}}

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