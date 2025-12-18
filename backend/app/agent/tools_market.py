import requests

BASE = "https://api.coingecko.com/api/v3"

def cg_get(endpoint, params=None):
    r = requests.get(f"{BASE}{endpoint}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# 메이저 코인 매핑
MAJOR_SYMBOL_MAP = {
    # 비트코인
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "비트코인": "bitcoin",

    # 이더리움
    "eth": "ethereum",
    "ethereum": "ethereum",
    "이더리움": "ethereum",

    # 테더
    "usdt": "tether",
    "tether": "tether",
    "테더" : "tether",

    # BNB
    "bnb": "binancecoin",
    "바이낸스코인": "binancecoin",

    # 솔라나
    "sol": "solana",
    "solana": "solana",
    "솔라나": "solana",

    # 리플
    "xrp": "ripple",
    "ripple": "ripple",
    "리플": "ripple",

    # USDC
    "usdc": "usd-coin",

    # 에이다
    "ada": "cardano",
    "cardano": "cardano",
    "에이다": "cardano",

    # 도지
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "도지": "dogecoin",
    "도지코인": "dogecoin",

    # 톤
    "ton": "toncoin",
    "toncoin": "toncoin",
    "톤코인": "toncoin",

    # 아발란체
    "avax": "avalanche-2",
    "아발란체" : "avalanche-2",

    # 트론
    "trx": "tron",
    "tron": "tron",
    "트론": "tron",

    # 체인링크
    "link": "chainlink",
    "chainlink": "chainlink",
    "체인링크": "chainlink",

    # 폴카닷
    "dot": "polkadot",
    "polkadot": "polkadot",
    "폴카닷": "polkadot",

    # 비트코인 캐시
    "bch": "bitcoin-cash",
    "bitcoin cash": "bitcoin-cash",
    "비트코인 캐시": "bitcoin-cash",

    # 라이트코인
    "ltc": "litecoin",
    "litecoin": "litecoin",
    "라이트 코인" : "litecoin",

    # 폴리곤 / 매틱
    "matic": "matic-network",
    "polygon": "matic-network",
    "폴리곤": "matic-network",
    "매틱": "matic-network",

    # 유니스왑
    "uni": "uniswap",
    "유니스왑" : "uniswap",

    # 이더리움 클래식
    "etc": "ethereum-classic",
    "이더리움 클래식" : "ethereum-classic",

    # 스택스
    "stx": "stacks",
    "스택스" : "stacks",

    # 옵티미즘
    "op": "optimism",
    "옵티미즘" : "optimism",

    # 아비트럼
    "arb": "arbitrum",
    "아비트럼" : "arbitrum",

    # 인젝티브
    "inj": "injective-protocol",
    "인젝티브" : "injective-protocol",

    # 앱토스
    "apt": "aptos",
    "앱토스" : "aptos",

    # 수이
    "sui": "sui",
    "수이": "sui",

    # 세이
    "sei": "sei-network",
    "세이": "sei-network",

    # 페페
    "pepe": "pepe",
    "페페": "pepe",

    # 시바이누
    "shib": "shiba-inu",
    "shiba": "shiba-inu",
    "shiba inu": "shiba-inu",
    "시바": "shiba-inu",
    "시바이누": "shiba-inu",

    # dogwifhat
    "wif": "dogwifcoin",
    "dogwifhat": "dogwifcoin",
    "도지" : "dogwifcoin",
    "도지코인" : "dogwifcoin",
    "도지 코인" : "dogwifcoin",

    # bonk
    "bonk": "bonk",
}


# id 변환
import re

def normalize_symbol(text: str) -> str:
    """
    사용자의 자연어 문장에서 코인 심볼/이름을 뽑아서
    CoinGecko id로 변환
    """

    lower = text.lower()

    # 1단계: 완전 일치(문장 전체가 코인명인 경우)
    if lower in MAJOR_SYMBOL_MAP:
        return MAJOR_SYMBOL_MAP[lower]

    # 2단계: 단어 단위로 쪼개서 찾기 (BTC, 비트코인, solana 등)
    tokens = re.findall(r"[a-z0-9\-]+|[가-힣]+", lower)

    for t in tokens:
        if t in MAJOR_SYMBOL_MAP:
            return MAJOR_SYMBOL_MAP[t]

    # 여기까지 못 찾으면 에러
    raise ValueError(f"지원하지 않는 코인입니다: {text}")

# 단일 코인 가격
def get_price(symbol):
    coin_id = normalize_symbol(symbol)

    data = cg_get(
        "/coins/markets",
        params={
            "vs_currency":"usd",
            "ids":coin_id,
        }
    )

    if not data:
        raise ValueError(f"No CoinGecko response for symbol: {symbol}")

    d = data[0]

    return {
        "symbol": d["symbol"].upper(),
        "name": d["name"],
        "price_usd": d["current_price"],
        "change_24h": d["price_change_percentage_24h"],
        "market_cap": d["market_cap"],
        "rank": d["market_cap_rank"],
    }


# 24시간 통계
def get_24h_stats(symbol: str):
    coin_id = normalize_symbol(symbol)
    
    data = cg_get(
        "/coins/markets",
        params = {
            "vs_currency" : "usd",
            "ids" : coin_id,
        }
    )[0]

    return {
        "symbol": data["symbol"].upper(),
        "open": data["current_price"] / (1 + data["price_change_percentage_24h"]/100),
        "high_24h": data["high_24h"],
        "low_24h": data["low_24h"],
        "close": data["current_price"],
        "change_percent": data["price_change_percentage_24h"],
        "volume_24h": data["total_volume"]
    }


# 다종목 비교
def compare_symbols(symbols: list[str]):
    ids = ",".join(normalize_symbol(s) for s in symbols)

    results = cg_get(
        "/coins/markets",
        params = {
            "vs_currency" : "usd",
            "ids" : ids
        }
    )

    return [
        {
            "symbol": c["symbol"].upper(),
            "price": c["current_price"],
            "change_24h": c["price_change_percentage_24h"],
            "rank": c["market_cap_rank"]
        }
        for c in results
    ]


# 급등락 종목
def get_top_movers(top_n=5):

    results = cg_get(
        "/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "price_change_percentage_24h_desc",
            "per_page": top_n,
            "page": 1
        }
    )

    return [
        {
            "symbol": c["symbol"].upper(),
            "name": c["name"],
            "price": c["current_price"],
            "change_24h": c["price_change_percentage_24h"]
        }
        for c in results
    ]


# 시총 + 랭킹

def get_market_cap(symbol: str):
    coin_id = normalize_symbol(symbol)
    data = cg_get(
        "/coins/markets",
        params={
            "vs_currency":"usd",
            "ids":coin_id
        }
    )[0]

    return {
        "symbol": data["symbol"].upper(),
        "name": data["name"],
        "market_cap": data["market_cap"],
        "rank": data["market_cap_rank"],
        "volume_24h": data["total_volume"]
    }


# 트랜딩
def get_trending_coins():

    coins = cg_get("/search/trending")["coins"]

    return [
        {
            "symbol": c["item"]["symbol"],
            "name": c["item"]["name"],
            "rank": c["item"]["market_cap_rank"]
        }
        for c in coins
    ]

# 종합 시장 스냅샷
def get_market_snapshot():

    global_data = cg_get("/global")["data"]

    top_movers = get_top_movers(5)

    return {
        "global_market":{
            "total_market_cap_usd": global_data["total_market_cap"]["usd"],
            "total_volume_24h_usd": global_data["total_volume"]["usd"],
            "btc_dominance": global_data["market_cap_percentage"]["btc"]
        },
        "top_movers": top_movers
    }

