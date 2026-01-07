// src/components/trade/TopStats.jsx
import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import CryptoJS from 'crypto-js';

import useUpbitData from './services/Upbit'
import { RSI, MACD } from 'technicalindicators';

const coinIcons = {
    BTC: "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=025",
    ETH: "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=025",
    XRP: "https://cryptologos.cc/logos/xrp-xrp-logo.png?v=025",
    BCH: "https://cryptologos.cc/logos/bitcoin-cash-bch-logo.png",
    USDT: "https://cryptologos.cc/logos/tether-usdt-logo.png?v=025",
};

const API_CONFIG = {
    "uri": "/openApi/swap/v2/user/positions",
    "method": "GET",
    "payload": { "symbol": "BTC-USDT" },
};

function getParameters(API, timestamp, urlEncode = false) {
    let parameters = "";
    for (const key in API.payload) {
        if (Object.prototype.hasOwnProperty.call(API.payload, key)) {
            const value = API.payload[key];
            if (urlEncode) {
                parameters += key + "=" + encodeURIComponent(value) + "&";
            } else {
                parameters += key + "=" + value + "&";
            }
        }
    }
    if (parameters) {
        parameters = parameters.substring(0, parameters.length - 1);
        parameters = parameters + "&timestamp=" + timestamp;
    } else {
        parameters = "timestamp=" + timestamp;
    }
    return parameters;
}

async function fetchBingXPositions(API_KEY, API_SECRET) {
    if (!API_KEY || !API_SECRET) throw new Error("API Key/Secret이 설정되지 않았습니다.");
    const timestamp = new Date().getTime();
    const parameterString = getParameters(API_CONFIG, timestamp);
    const sign = CryptoJS.enc.Hex.stringify(CryptoJS.HmacSHA256(parameterString, API_SECRET));
    const url = API_CONFIG.uri + "?" + getParameters(API_CONFIG, timestamp, true) + "&signature=" + sign;

    const config = {
        method: API_CONFIG.method,
        url: `/bingx${url}`, 
        headers: { 'X-BX-APIKEY': API_KEY },
        transformResponse: (resp) => {
            const jsonWithBigIntToString = resp.replace(/:(\d{15,})(?=[,}\]])/g, (_, p1) => `:"${p1}"`);
            try { return JSON.parse(jsonWithBigIntToString); } 
            catch (e) { return { code: -1, msg: "JSON 파싱 오류" }; }
        }
    };
    const resp = await axios(config);
    return resp.data;
}

export default function TopStats({ isLogin, walletData, user_information }) {
    const prevWalletRef = useRef(null);
    const [positionData, setPositionData] = useState([]);
    const [loadingPositions, setLoadingPositions] = useState(true);
    const [positionError, setPositionError] = useState(null);
    const [API_KEY, setapikey] = useState("")
    const [API_SECRET, setapisecert] =  useState("")
    const [isexchange, setIsExChange] = useState(false)
    const [holdingData, setHoldingData] = useState([])
    const [historyData, setHistoryData] = useState([])
    const currentPrice = useUpbitData(walletData && Object.keys(walletData).length ? walletData : null);

    const [statsData, setStatsData] = useState({
        m15: { rsi: 0, rsiStatus: "-", macd: 0, macdSignal: 0 },
        h4: { rsi: 0, rsiStatus: "-", macd: 0, macdSignal: 0 }
    });

    useEffect(() => {
        const updateIndicators = async () => {
            try {
                const fetchK = async (iv) => {
                    const res = await axios.get(`https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=${iv}&limit=100`);
                    return res.data.map(d => parseFloat(d[4]));
                };
                const [c15m, c4h] = await Promise.all([fetchK("15m"), fetchK("4h")]);

                const r15 = RSI.calculate({ values: c15m, period: 14 }).pop() || 0;
                const r4 = RSI.calculate({ values: c4h, period: 14 }).pop() || 0;
                const m15 = MACD.calculate({ values: c15m, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }).pop() || { MACD: 0, signal: 0 };
                const m4 = MACD.calculate({ values: c4h, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }).pop() || { MACD: 0, signal: 0 };

                setStatsData({
                    m15: {
                        rsi: r15,
                        rsiStatus: r15 >= 70 ? "과매수" : r15 <= 30 ? "과매도" : "보통",
                        macd: m15.MACD,
                        macdSignal: m15.signal
                    },
                    h4: {
                        rsi: r4,
                        rsiStatus: r4 >= 70 ? "과매수" : r4 <= 30 ? "과매도" : "보통",
                        macd: m4.MACD,
                        macdSignal: m4.signal
                    }
                });
            } catch (e) { console.error(e); }
        };
        updateIndicators();
        const timer = setInterval(updateIndicators, 60000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        setapikey(user_information['bingx_access_key'])
        setapisecert(user_information['bingx_secret_key'])
        let isExChange = false;
        if (walletData && Object.values(walletData).some(value => value > 0)) isExChange = true;
        setIsExChange(isExChange);
    },[walletData])

    useEffect(() => {
        if (!isLogin) {
             setPositionData([]); setLoadingPositions(false); setPositionError(null); return; 
        }
        const fetchAndSetPositions = () => {
             fetchBingXPositions(API_KEY, API_SECRET).then(result => {
                if (result.code === 0) {
                    const transformedData = (result.data || []).map(pos => {
                        const unrealizedProfit = parseFloat(pos.unrealizedProfit);
                        const realizedProfit = parseFloat(pos.realisedProfit);
                        return {
                            coin: pos.symbol.split('-')[0], 
                            type: pos.positionSide === 'LONG' ? '매수' : '매도', 
                            entry: parseFloat(pos.avgPrice).toLocaleString(), 
                            amount: parseFloat(pos.positionAmt).toLocaleString(undefined, { maximumFractionDigits: 4 }), 
                            pnl: `${unrealizedProfit >= 0 ? '+' : ''}${unrealizedProfit.toFixed(4)}`, 
                            realizedPnl: `${realizedProfit >= 0 ? '+' : ''}${realizedProfit.toFixed(4)}`, 
                            liquidationPrice: parseFloat(pos.liquidationPrice).toFixed(1), 
                            isWin: unrealizedProfit >= 0,
                            isRealizedWin: realizedProfit >= 0,
                            leverage: pos.leverage,
                        };
                    });
                    setPositionData(transformedData); setPositionError(null);
                } else { setPositionError(`API 오류: ${result.msg}`); }
            }).catch(err => { setPositionError(`로드 실패: ${err.message}`); }).finally(() => { setLoadingPositions(false); });
        };
        fetchAndSetPositions();
        const intervalId = setInterval(fetchAndSetPositions, 3000); 
        return () => clearInterval(intervalId);
    }, [API_KEY, API_SECRET, isLogin]); 

    useEffect(() => {
        if (!walletData) return;
        if (prevWalletRef.current && JSON.stringify(prevWalletRef.current) === JSON.stringify(walletData)) return;
        prevWalletRef.current = walletData;
        const th = walletData.trade_history || {};
        const formatLocalTime = (isoTime) => {
            if (!isoTime) return "N/A";
            const date = new Date(isoTime);
            return `${String(date.getFullYear()).slice(2)}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        };
        setHistoryData([
            { time: formatLocalTime(th?.['BTC']?.created_at), coin: "BTC", type: th?.['BTC']?.side, qty: th?.['BTC']?.executed_volume || 0, isBuy: true },
            { time: formatLocalTime(th?.['ETH']?.created_at), coin: "ETH", type: th?.['ETH']?.side, qty: th?.['ETH']?.executed_volume || 0, isBuy: false },
            { time: formatLocalTime(th?.['XRP']?.created_at), coin: "XRP", type: th?.['XRP']?.side, qty: th?.['XRP']?.executed_volume || 0, isBuy: true },
            { time: formatLocalTime(th?.['BCH']?.created_at), coin: "BCH", type: th?.['BCH']?.side, qty: th?.['BCH']?.executed_volume || 0, isBuy: false },
        ]);
    }, [walletData]);

    useEffect(() => {
        if (!currentPrice) return;
        const oc = walletData.owner_coin || {};
        const newOwnerValue = {};
        Object.keys(oc).forEach((coin) => {
            newOwnerValue[coin] = Math.floor((oc[coin] || 0) * (currentPrice[coin] || 0));
        });
        const coinOrder = ["BTC", "ETH", "XRP", "BCH"];
        setHoldingData(coinOrder.map((coin) => ({
            coin, amount: oc[coin] || 0, value: newOwnerValue[coin] || 0, isWin: coin === "BTC" || coin === "ETH",
        })));
    }, [currentPrice, walletData]);

    // --- 스타일 (Compact Version) ---
    const styles = {
        container: { width: '100%', height: '100%', display: 'flex', gap: '15px' },
        cardsArea: { flex: 0.6, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' },
        rightArea: { flex: 1.4, display: 'flex', gap: '10px', minWidth: 0 },
        
        indicatorCard: {
            backgroundColor: 'var(--trade-card-bg)',
            border: '1px solid var(--trade-border)',
            borderRadius: '8px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            display: 'flex',
            flexDirection: 'column',
            minHeight: '160px', // [수정] 최소 높이 줄임
            minWidth: 0,
            overflow: 'hidden', 
        },
        
        // [수정] 헤더 여백 축소
        cardHeader: {
            padding: '10px 12px', // 상하 패딩 12px -> 8px
            borderBottom: '1px solid var(--trade-border)',
            backgroundColor: 'var(--trade-bg)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
        },
        titleText: { fontSize: '0.85rem', fontWeight: '800', color: 'var(--trade-text)' },
        subTitle: { fontSize: '0.75rem', color: 'var(--trade-subtext)', fontWeight: 'bold' },

        // [수정] 콘텐츠 영역 여백 축소
        cardContent: {
            padding: '8px 10px', // 14px -> 8px
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            flex: 1, 
            gap: '4px', // 박스 간격 8px -> 4px
        },

        // [수정] 지표 박스 패딩 축소
        statBox: { 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '12px 10px', // 10px -> 6px
            borderRadius: '6px',
            backgroundColor: 'rgba(128, 128, 128, 0.05)',
            border: '1px solid rgba(128, 128, 128, 0.1)',
        },
        
        mainLabel: { fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--trade-subtext)' },
        
        valueContainer: { textAlign: 'right', display: 'flex', alignItems: 'center', gap: '8px' },
        
        mainValue: { fontSize: '0.95rem', fontWeight: '800', color: 'var(--trade-text)' }, // 폰트 사이즈 미세 조정

        getBadgeStyle: (status) => {
            let bgColor = '#9e9e9e'; 
            if (status === '과매수') bgColor = '#ef5350'; 
            if (status === '과매도') bgColor = '#26a69a'; 
            
            return {
                backgroundColor: bgColor,
                color: '#fff',
                padding: '2px 6px', // 패딩 미세 축소
                borderRadius: '10px',
                fontSize: '0.7rem',
                fontWeight: '600',
                display: 'inline-block',
                minWidth: '40px',
                textAlign: 'center',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
            };
        },

        // 우측 테이블 스타일 (기존 유지)
        historyBox: {
            flex: 1, backgroundColor: 'var(--trade-card-bg)',
            border: '1px solid var(--trade-border)', borderRadius: '6px',
            display: 'flex', flexDirection: 'column', overflow: 'hidden',
            boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
        },
        sectionHeader: {
            padding: '10px 12px', fontSize: '0.85rem', fontWeight: 'bold',
            borderBottom: '1px solid var(--trade-border)', backgroundColor: 'var(--trade-bg)',
            color: 'var(--trade-text)', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        },
        posHeader: { display: 'grid', gridTemplateColumns: '0.7fr 0.6fr 1fr 0.8fr 1fr 1fr 1fr', padding: '8px 0', fontSize: '0.7rem', fontWeight: 'bold', borderBottom: '1px solid var(--trade-border)', color: 'var(--trade-subtext)', textAlign: 'center' },
        holdHeader: { display: 'grid', gridTemplateColumns: '0.9fr 0.9fr 1.2fr', padding: '8px 0', fontSize: '0.7rem', fontWeight: 'bold', borderBottom: '1px solid var(--trade-border)', color: 'var(--trade-subtext)', textAlign: 'center' },
        histHeader: { display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1.5fr', padding: '8px 0', fontSize: '0.7rem', fontWeight: 'bold', borderBottom: '1px solid var(--trade-border)', color: 'var(--trade-subtext)', textAlign: 'center' },
        tableRow: { display: 'grid', padding: '8px 0', fontSize: '0.75rem', borderBottom: '1px solid var(--trade-border)', alignItems: 'center', textAlign: 'center' },
        coinWrapper: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px', fontWeight: 'bold' },
        coinIcon: { width: '14px', height: '14px', borderRadius: '50%' },
        badgeLong: { backgroundColor: 'rgba(8, 153, 129, 0.15)', color: '#089981', padding: '2px 4px', borderRadius: '3px', fontSize: '0.7rem', fontWeight: 'bold' },
        badgeShort: { backgroundColor: 'rgba(242, 54, 69, 0.15)', color: '#f23645', padding: '2px 4px', borderRadius: '3px', fontSize: '0.7rem', fontWeight: 'bold' },
        pnlWin: { color: '#089981', fontWeight: 'bold' },
        pnlLose: { color: '#f23645', fontWeight: 'bold' },
    };

    const getRsiColor = (val) => val >= 70 ? "#f23645" : val <= 30 ? "#089981" : "var(--trade-text)";

    // [1] 현물 포지션
    const renderPositionTable = () => (
        <div style={styles.historyBox}>
            <div style={styles.sectionHeader}>
                <span>⚡ 포지션 (선물)</span>
                {loadingPositions ? (
                    <span style={{fontSize:'0.7rem', color:'var(--trade-subtext)'}}>로딩 중...</span>
                ) : positionError ? (
                    <span style={{fontSize:'0.7rem', color:'red'}}>오류</span>
                ) : (
                    <span style={{fontSize:'0.7rem', color:'var(--trade-subtext)'}}>{positionData.length}건</span>
                )}
            </div>
            <div style={styles.posHeader}>
                <span>코인</span>
                <span>Side</span>
                <span>진입가</span>
                <span>수량</span> 
                <span>미실현</span> 
                <span>실현</span> 
                <span>청산가</span>
            </div>
            <div style={{overflowY:'auto', flex:1}} className="custom-scroll">
                {loadingPositions && (
                    <div style={{textAlign:'center', padding:'20px', color:'var(--trade-subtext)'}}>데이터를 불러오는 중...</div>
                )}
                {!loadingPositions && positionData.length === 0 && !positionError && (
                    <div style={{textAlign:'center', padding:'20px', color:'var(--trade-subtext)'}}>
                        현재 포지션이 없습니다.
                    </div>
                )}
                {positionData.map((pos, i) => (
                    <div key={i} style={{...styles.tableRow, gridTemplateColumns: '0.7fr 0.6fr 1fr 0.8fr 1fr 1fr 1fr'}}>
                        <div style={styles.coinWrapper}>
                            <img src={coinIcons[pos.coin] || coinIcons.USDT} alt="" style={styles.coinIcon} />
                            <span>{pos.coin}</span>
                        </div>
                        <div><span style={pos.type === '매수' ? styles.badgeLong : styles.badgeShort}>{pos.type}</span></div>
                        <span style={{color:'var(--trade-subtext)'}}>${pos.entry}</span>
                        <span style={{color:'var(--trade-text)'}}>{pos.amount}</span>
                        <span style={pos.isWin ? styles.pnlWin : styles.pnlLose}>{pos.pnl}</span>
                        <span style={pos.isRealizedWin ? styles.pnlWin : styles.pnlLose}>{pos.realizedPnl}</span> 
                        <span style={{color:'var(--trade-subtext)'}}>${pos.liquidationPrice}</span> 
                    </div>
                ))}
            </div>
        </div>
    );

    // [2] 현물 보유코인
    const renderHoldingTable = () => (
        <div style={styles.historyBox}>
            <div style={styles.sectionHeader}>
                <span>💰 보유 코인 (현물)</span>
            </div>
            {isexchange ? (
                <>
                    <div style={styles.holdHeader}>
                        <span>코인</span>
                        <span>수량</span>
                        <span>평가금</span>
                    </div>
                    <div style={{ overflowY: 'auto', flex: 1 }} className="custom-scroll">
                        {holdingData.map((hold, i) => (
                            <div key={i} style={{ ...styles.tableRow, gridTemplateColumns: '0.9fr 0.9fr 1.2fr' }}>
                                <div style={styles.coinWrapper}>
                                    <img src={coinIcons[hold.coin]} alt="" style={styles.coinIcon} />
                                    <span>{hold.coin}</span>
                                </div>
                                <span style={{ color: 'var(--trade-text)' }}>{hold.amount}</span>
                                <div style={{ fontWeight: 'bold', color: 'var(--trade-text)' }}>
                                    {Number(hold.value).toLocaleString()} ₩
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--trade-subtext)' }}>
                    거래소를 설정해 주세요.
                </div>
            )}
        </div>
    );

    // [3] 거래 내역
    const renderHistoryTable = () => (
        <div style={styles.historyBox}>
            <div style={styles.sectionHeader}>
                <span>📋 거래 내역 (현물)</span>
            </div>           
            {isexchange ? (             
                <>
                    <div style={styles.histHeader}>
                        <span>시간</span>
                        <span>코인</span>
                        <span>타입</span>
                        <span>수량</span>
                    </div>
                    <div style={{overflowY:'auto', flex:1}} className="custom-scroll">
                        {historyData.map((trade, i) => (
                            <div key={i} style={{...styles.tableRow, gridTemplateColumns: '2fr 1fr 1fr 1.5fr'}}>
                                <span style={{color:'var(--trade-subtext)', fontSize:'0.7rem'}}>{trade.time}</span>
                                <div style={styles.coinWrapper}>
                                    <img src={coinIcons[trade.coin]} alt="" style={styles.coinIcon} />
                                    <span>{trade.coin}</span>
                                </div>
                                <div>
                                    <span style={trade.type == "bid" ? styles.badgeLong : styles.badgeShort}>{trade.type}</span>
                                </div>
                                <span style={{color:'var(--trade-text)'}}>{trade.qty}</span>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--trade-subtext)' }}>
                    거래소를 설정해 주세요.
                </div>
            )}
        </div>
    );

    return (
        <div style={styles.container}>
            {/* 좌측: 지표 카드 2개 (좌우 배치) */}
            <div style={styles.cardsArea}>
                
                {/* 15분 카드 */}
                <div style={styles.indicatorCard}>
                    {/* Header */}
                    <div style={styles.cardHeader}>
                        <span style={styles.titleText}>15분</span>
                        <span style={styles.subTitle}>BTC</span>
                    </div>
                    
                    <div style={styles.cardContent}>
                        {/* RSI - 박스형 + 뱃지 */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>RSI</span>
                            <div style={styles.valueContainer}>
                                {/* 상태 뱃지 */}
                                <span style={styles.getBadgeStyle(statsData.m15.rsiStatus)}>
                                    {statsData.m15.rsiStatus}
                                </span>
                                <span style={{...styles.mainValue, color: getRsiColor(statsData.m15.rsi)}}>
                                    {statsData.m15.rsi.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* MACD */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>MACD</span>
                            <div style={styles.valueContainer}>
                                <span style={styles.mainValue}>
                                    {statsData.m15.macd.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* Signal Line */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>Signal Line</span>
                            <div style={styles.valueContainer}>
                                <span style={styles.mainValue}>
                                    {statsData.m15.macdSignal.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 4시간 카드 */}
                <div style={styles.indicatorCard}>
                    {/* Header */}
                    <div style={styles.cardHeader}>
                        <span style={styles.titleText}>4시간</span>
                        <span style={styles.subTitle}>BTC</span>
                    </div>
                    
                    <div style={styles.cardContent}>
                        {/* RSI */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>RSI</span>
                            <div style={styles.valueContainer}>
                                <span style={styles.getBadgeStyle(statsData.h4.rsiStatus)}>
                                    {statsData.h4.rsiStatus}
                                </span>
                                <span style={{...styles.mainValue, color: getRsiColor(statsData.h4.rsi)}}>
                                    {statsData.h4.rsi.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* MACD */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>MACD</span>
                            <div style={styles.valueContainer}>
                                <span style={styles.mainValue}>
                                    {statsData.h4.macd.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* Signal Line */}
                        <div style={styles.statBox}>
                            <span style={styles.mainLabel}>Signal Line</span>
                            <div style={styles.valueContainer}>
                                <span style={styles.mainValue}>
                                    {statsData.h4.macdSignal.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            
            {/* 우측 테이블 영역 */}
            <div style={styles.rightArea}>
                {isLogin ? (
                    <>
                        {renderPositionTable()}
                        {renderHoldingTable()}
                        {renderHistoryTable()}
                    </>
                ) : (
                    <div style={{...styles.historyBox, alignItems:'center', justifyContent:'center'}}>
                        <h3 style={{margin:'0 0 5px 0', fontSize:'1rem'}}>로그인 후 사용하실 수 있습니다</h3>
                    </div>
                )}
            </div>
        </div>
    );
}