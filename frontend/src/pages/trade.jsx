// src/pages/trade.jsx

import React, { useState, useEffect, useMemo } from 'react';
import "../styles/pages/trade.css";

import Header from "../components/common/Header.jsx";
import Footer from "../components/common/Footer.jsx";
import TopStats from "../components/trade/TopStats.jsx";
import ChatBot from "../components/trade/ChatBot.jsx";
import TradingViewWidget from "../components/trade/TradingViewWidget.jsx";
import TradeData from './services/Trade_Data';

//service
import {User_Information, User_Infor_Modify} from '../services/user_inforamtion.jsx'


export default function TradePage({ darkMode, setDarkMode, verify, Username }) {
    const [isLogin, setIsLogin] = useState(false);
    const [symbol, setSymbol] = useState("BINANCE:BTCUSDT");
        
    // 데이터 상태
    const [marketData, setMarketData] = useState([]); 
    const [myWatchlist, setMyWatchlist] = useState(["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT"]); 
    const [favorites, setFavorites] = useState(new Set(["BTCUSDT"]));
    
    // UI 상태
    const [searchTerm, setSearchTerm] = useState("");
    const [viewMode, setViewMode] = useState("all");
    const [isChatOpen, setIsChatOpen] = useState(false); 

    const [sender_chartData, setChartData] = useState([]);
    const [sender_walletData, setWalletData] = useState([]);
    const [sender_analzeData, setAnalzeData] = useState([]);

    const [userinfo, setUserInfo] = useState({});

    // 거래대금 포맷팅 함수
    const formatVolume = (numStr) => {
        if (!numStr) return "0.00";
        const num = parseFloat(numStr);
        if (isNaN(num)) return "0.00";
        
        if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
        if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
        if (num >= 1e3) return (num / 1e3).toFixed(2) + "K";
        return num.toFixed(2);
    };

    // 추가된 부분
    useEffect(() => {
        if (verify === "verified"){
            setIsLogin(true)
        }
    }, [verify]);

    // 추가된 부분
    useEffect(() => {
        const loadUser = async () => {
          const userinfo = await User_Information();
            
          if (!userinfo) return;
          else {
            setUserInfo(userinfo)
          }
        };

        loadUser();
    },[])
    
    useEffect(() => {
        const interval = setInterval(async () => {
        const { chartData, walletData, analzeData } = await TradeData();
        
        if (JSON.stringify(chartData) !== JSON.stringify(sender_chartData)) {
            setChartData(chartData);
        }
        if (JSON.stringify(walletData) !== JSON.stringify(sender_walletData)) {
            setWalletData(walletData);
        }
        if (JSON.stringify(analzeData) !== JSON.stringify(sender_analzeData)) {
            setAnalzeData(analzeData);
        }
        }, 1000);

        return () => clearInterval(interval); 
    }, []);
    
    useEffect(() => {
        const loginState = localStorage.getItem("isLogin") === "true";
        setIsLogin(loginState);

        const fetchMarketData = async () => {
            try {
                const res = await fetch("https://api.binance.com/api/v3/ticker/24hr");
                const data = await res.json();
                
                const formattedData = data
                    .filter(item => item.symbol.endsWith("USDT"))
                    .map(item => ({
                        s: item.symbol,
                        p: parseFloat(item.lastPrice).toLocaleString(undefined, { maximumFractionDigits: 4 }),
                        c: parseFloat(item.priceChangePercent).toFixed(2) + "%",
                        v: formatVolume(item.quoteVolume), 
                        up: parseFloat(item.priceChangePercent) > 0
                    }));
                
                setMarketData(formattedData);
            } catch (err) { console.error("API Error:", err); }
        };

        fetchMarketData();
        const interval = setInterval(fetchMarketData, 5000); 
        return () => clearInterval(interval);
    }, []);

    const displayList = useMemo(() => {
        if (searchTerm.trim() !== "") {
            return marketData.filter(coin => coin.s.includes(searchTerm.toUpperCase())).slice(0, 50);
        }
        const myCoins = marketData.filter(coin => myWatchlist.includes(coin.s));
        if (viewMode === 'fav') return myCoins.filter(coin => favorites.has(coin.s));
        return myCoins;
    }, [searchTerm, marketData, myWatchlist, viewMode, favorites]);

    const handleCoinClick = (coinSymbol) => {
        setSymbol(`BINANCE:${coinSymbol}`);
        if (searchTerm !== "") {
            if (!myWatchlist.includes(coinSymbol)) setMyWatchlist(prev => [coinSymbol, ...prev]);
            setSearchTerm("");
        }
    };

    const toggleFavorite = (e, coinSymbol) => {
        e.stopPropagation();
        setFavorites(prev => {
            const newFavs = new Set(prev);
            if (newFavs.has(coinSymbol)) newFavs.delete(coinSymbol);
            else newFavs.add(coinSymbol);
            return newFavs;
        });
    };

        
    return (
        <div className="trade-container">
            <div className="area-header">
                <Header darkMode={darkMode} setDarkMode={setDarkMode} isLogin={isLogin} verify = {verify} Username = {Username} />
            </div>

            <div className="area-top-stats">
                <TopStats isLogin={isLogin} analzeData={sender_analzeData} walletData = {sender_walletData} user_information={userinfo} />
            </div>

            <div className="area-main">
                <div className="chart-box">
                    <TradingViewWidget darkMode={darkMode} symbol={symbol} /> 
                </div>

                <div className="side-panel-box">
                    {isChatOpen ? (
                        <div className="chat-mode-container">
                            <div className="panel-title">
                                <span>AI Chat Assistant</span>
                            </div>
                            <div className="chat-content-area">
                                <ChatBot />
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="list-header-search">
                                <div className="search-tabs">
                                    <button className={`s-tab ${viewMode === 'all' ? 'active' : ''}`} onClick={() => setViewMode('all')}>관심종목</button>
                                    <button className={`s-tab ${viewMode === 'fav' ? 'active' : ''}`} onClick={() => setViewMode('fav')}>★</button>
                                </div>
                                <div className="search-input-wrapper">
                                    <i className="fa-solid fa-magnifying-glass search-icon"></i>
                                    <input 
                                        type="text" 
                                        className="coin-search-input" 
                                        placeholder="코인 검색 (예: BTC)"
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="column-labels">
                                <span>{searchTerm ? "검색 결과" : "코인명"}</span>
                                <span>현재가</span>
                                <span>변동률</span>
                                <span>거래대금</span>
                            </div>

                            <div className="list-content">
                                {displayList.length > 0 ? (
                                    displayList.map((coin) => (
                                        <div key={coin.s} className="list-row" onClick={() => handleCoinClick(coin.s)}>
                                            <div className="symbol-col">
                                                <span className={`fav-star ${favorites.has(coin.s) ? 'active' : ''}`} onClick={(e) => toggleFavorite(e, coin.s)}>
                                                    {favorites.has(coin.s) ? '★' : '☆'}
                                                </span>
                                                <span className="coin-name">{coin.s.replace('USDT', '')}</span>
                                                <span className="coin-pair">/USDT</span>
                                            </div>
                                            <span className={coin.up ? "text-up" : "text-down"}>{coin.p}</span>
                                            <span className={`badge ${coin.up ? "bg-up" : "bg-down"}`}>{coin.c}</span>
                                            <span style={{color: 'var(--trade-subtext)', fontSize: '0.75rem'}}>
                                                {coin.v}
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="empty-msg">
                                        {searchTerm ? "검색 결과가 없습니다." : "리스트가 비어있습니다."}
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>

            <button 
                className="chat-float-btn" 
                onClick={() => setIsChatOpen(!isChatOpen)}
                title={isChatOpen ? "관심종목 보기" : "AI 챗봇 열기"}
            >
                {isChatOpen ? <i className="fa-solid fa-list-ul"></i> : <i className="fa-solid fa-robot"></i>}
            </button>

            <div className="area-footer">
                <Footer />
            </div>
        </div>
    );
}