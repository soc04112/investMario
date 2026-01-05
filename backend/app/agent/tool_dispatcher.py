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
    """
    tool_call = {
      "name": "get_latest_strategy",
      "arguments": {...}
    }
    """

    name = tool_call.get("name")
    args = tool_call.get("arguments", {})

    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {name}"}

    # 🔐 userid 강제 주입 (LLM이 주지 않아도 서버가 넣음)
    if "userid" in TOOL_REGISTRY[name].__code__.co_varnames:
        args["userid"] = userid

    try:
        result = TOOL_REGISTRY[name](**args)
        return result
    except Exception as e:
        return {"error": str(e)}
