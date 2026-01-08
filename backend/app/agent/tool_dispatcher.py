import json

# 실제 함수들 import
from app.agent.tools_market import *
from app.agent.tools_news import *
from app.agent.tools_terms import *
from app.agent.tools_portfolio import *

# 허용된 함수만 등록 (화이트리스트)
TOOL_REGISTRY = {
    "get_price": get_price,
    "get_price_by_date": get_price_by_date,
    "get_24h_stats": get_24h_stats,
    "compare_symbols": compare_symbols,
    "get_top_movers": get_top_movers,
    "get_market_cap": get_market_cap,
    "get_trending_coins": get_trending_coins,
    "get_market_snapshot": get_market_snapshot,
    "get_crypto_news": get_crypto_news,
    "search_crypto_term": search_crypto_term,
    "get_user_profile": get_user_profile,
    "get_latest_strategy": get_latest_strategy,
    "get_strategy_by_date": get_strategy_by_date,
}

def dispatch_tool(tool_call: dict, userid: str):
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})

    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {name}"}

    # 🔐 중요: TOOL_REGISTRY에 등록된 함수(예: get_user_profile)가 
    # 인자로 'userid'를 받는지 확인하고 서버 세션의 userid를 강제 주입합니다.
    import inspect
    sig = inspect.signature(TOOL_REGISTRY[name])
    if "userid" in sig.parameters:
        args["userid"] = userid

    try:
        # 도구 실행 (get_user_profile(userid="U123...") 호출됨)
        result = TOOL_REGISTRY[name](**args)
        return result
    except Exception as e:
        return {"error": str(e)}
