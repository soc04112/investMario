from app.agent.tools_market import *
from app.agent.tools_news import *
from app.agent.tools_terms import *
from app.agent.tools_portfolio import *

TOOL_REGISTRY = {
    "get_price": get_price,
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
