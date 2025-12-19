TOOLS_SCHEMA = [

# ------------------------
#  MARKET DATA TOOLS
# ------------------------

{
    "type": "function",
    "function": {
        "name": "get_price",
        "description": "Get real-time crypto price and market cap",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"}
            },
            "required": ["symbol"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_24h_stats",
        "description": "Get 24-hour trading statistics",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"}
            },
            "required": ["symbol"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "compare_symbols",
        "description": "Compare TWO OR MORE cryptocurrencies. Use this function when the user asks to compare multiple coins (e.g. '비트코인과 이더리움 비교'). DO NOT use get_price in this case.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["symbols"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_top_movers",
        "description": "Get top price gainers",
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "default": 5}
            }
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_market_cap",
        "description": "Get market capitalization data",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"}
            },
            "required": ["symbol"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_trending_coins",
        "description": "Get trending coins",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_market_snapshot",
        "description": "Get overall crypto market snapshot",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
},

# ------------------------
#  NEWS TOOL (RAG)
# ------------------------

{
    "type": "function",
    "function": {
        "name": "get_crypto_news",
        "description": "Search latest crypto news from RAG DB",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
},

# ------------------------
#  ECONOMIC TERM TOOL (RAG)
# ------------------------

{
    "type": "function",
    "function": {
        "name": "search_crypto_term",
        "description": "Search crypto/economic terminology definitions from RAG database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 3}
            },
            "required": ["query"]
        }
    }
},

# ------------------------
#  PORTFOLIO DB TOOLS
# ------------------------

{
    "type": "function",
    "function": {
        "name": "get_user_profile",
        "description": "Fetch full user profile from portfolio DB",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_latest_strategy",
        "description": "Fetch the latest N trading strategy records",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 5}
            },
            "required": []
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_strategy_by_date",
        "description": "Fetch trading history filtered by date or date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO8601 start date"
                },
                "end_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO8601 end date (optional)"
                }
            },
            "required": ["start_date"]
        }
    }
}

]
