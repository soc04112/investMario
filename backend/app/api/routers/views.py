# backend/utils/views.py

from fastapi import APIRouter
from tradingview_ta import TA_Handler, Interval, Exchange

# 1. 라우터 생성
router = APIRouter()

# 2. 엔드포인트 등록 (URL: /api/bitcoin/analysis)
@router.get("/bitcoin/analysis")
def get_bitcoin_analysis():
    # 분석할 타임프레임 정의
    timeframes = {
        "15m": Interval.INTERVAL_15_MINUTES, # 키 값을 영어로 하는게 프론트에서 다루기 편합니다
        "4h": Interval.INTERVAL_4_HOURS,
        "1d": Interval.INTERVAL_1_DAY
    }
    
    symbol = "BTCUSDT"
    exchange = "BINANCE"
    results = {}

    for label, tf in timeframes.items():
        try:
            handler = TA_Handler(
                symbol=symbol,
                exchange=exchange,
                screener="crypto",
                interval=tf
            )
            analysis = handler.get_analysis()
            
            # 지표 추출
            rsi = analysis.indicators["RSI"]
            macd = analysis.indicators["MACD.macd"]
            stoch_k = analysis.indicators["Stoch.K"]
            
            # 상태 판별 로직 (RSI 기준)
            status = "안정"
            # 프론트엔드 스타일과 맞추기 위해 색상 코드 대신 상태값만 전달하거나,
            # 혹은 프론트에서 쓸 클래스명 전달
            
            if rsi >= 70:
                status = "과매수"
            elif rsi <= 30:
                status = "과매도"
                
            # 결과 저장
            results[label] = {
                "rsi": round(rsi, 2),
                "macd": round(macd, 2),
                "stoch_k": round(stoch_k, 2),
                "status": status,
            }
            
        except Exception as e:
            print(f"{label} 데이터 로딩 실패: {e}")
            results[label] = None
            
    return results