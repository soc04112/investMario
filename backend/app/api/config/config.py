from app.common.imports import *

from sqlalchemy import create_engine, Column, BigInteger, Text, Numeric, text, TIMESTAMP, JSON, DateTime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker




GOOGLE_CLOUDE_KEY = os.getenv("GOOGLE_CLOUDE_KEY")
print(GOOGLE_CLOUDE_KEY)
GOOGLE_CLOUDE_IP = os.getenv("GOOGLE_CLOUDE_IP")

DB_CONFIG = {
    "host" : GOOGLE_CLOUDE_IP,
    "port" : 5432,
    "database" : "postgres",
    "user" : "writer",
    "password" : GOOGLE_CLOUDE_KEY
}

DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TradingHistory(Base):
    __tablename__ = "trading_history"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="내부 식별자 Insert 순서 == 타임 테이블")
    
    userid = Column(Text, comment="유저 아이디")
    
    trade_number = Column(BigInteger, comment="거래 번호")

    time = Column(DateTime(timezone=True), comment="거래 시간")

    why = Column(JSONB, comment="코인 포지션 사유")

    position = Column(JSONB, comment="코인 포지션")

    average = Column(JSONB, comment="코인 평단가")

    available = Column(BigInteger, comment="이용 가능 금액")

    owner_coin = Column(JSONB, comment="보유 코인")

    total_asset = Column(BigInteger, comment="총 자산")
    
    trade = Column(JSONB, comment="거래 정보")

    trade_fee = Column(Numeric, comment="총 거래 수수료")

# 유저 정보
class UserInformation(Base):
    __tablename__ = "user_information"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="내부 식별자 Insert 순서 == 타임 테이블")
    
    userid = Column(Text, comment="유저 아이디")
    
    userinfo = Column(JSONB, comment="유저 정보")

    usercustom = Column(JSONB, comment="커스텀 정보")

    money = Column(JSONB, comment="돈 관련")

    key = Column(JSONB, comment="엑세스 키")
