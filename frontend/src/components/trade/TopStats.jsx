// src/components/trade/TopStats.jsx
import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import CryptoJS from 'crypto-js';

import useUpbitData from './services/Upbit'
import { RSI, MACD } from 'technicalindicators';

// 코인 아이콘
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
    "payload": {
        "symbol": "BTC-USDT" // 원하는 심볼로 변경 가능
    },
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

    if (!API_KEY || !API_SECRET) {
        throw new Error("API Key/Secret이 설정되지 않았습니다.");
    }

    const timestamp = new Date().getTime();

    // 1. Signature 생성
    const parameterString = getParameters(API_CONFIG, timestamp);
    const sign = CryptoJS.enc.Hex.stringify(CryptoJS.HmacSHA256(parameterString, API_SECRET));

    // 2. 최종 URL 생성 (프록시 경로를 사용: /api + URI + 쿼리)
    const url = 
        API_CONFIG.uri + 
        "?" + 
        getParameters(API_CONFIG, timestamp, true) + 
        "&signature=" + sign;

    const config = {
        method: API_CONFIG.method,
        url: `/bingx${url}`, 
        headers: {
            'X-BX-APIKEY': API_KEY,
        },
        transformResponse: (resp) => {
            // BigInt 이슈 처리 (15자리 이상 숫자를 문자열로 변환하여 파싱)
            const jsonWithBigIntToString = resp.replace(/:(\d{15,})(?=[,}\]])/g, (_, p1) => `:"${p1}"`);
            try {
                 return JSON.parse(jsonWithBigIntToString);
            } catch (e) {
                 console.error("JSON 파싱 오류", e);
                 return { code: -1, msg: "JSON 파싱 오류", originalResponse: resp }; 
            }
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
    // Upbit Current Price Data
    const currentPrice = useUpbitData(walletData && Object.keys(walletData).length ? walletData : null);

    useEffect(() => {
        const updateIndicators = async () => {
            try {
                const fetchK = async (iv) => {
                    const res = await axios.get(`https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=${iv}&limit=100`);
                    return res.data.map(d => parseFloat(d[4]));
                };

                const [c15m, c4h] = await Promise.all([fetchK("15m"), fetchK("4h")]);

                // 지표 계산
                const r15 = RSI.calculate({ values: c15m, period: 14 }).pop() || 0;
                const r4 = RSI.calculate({ values: c4h, period: 14 }).pop() || 0;
                const m15 = MACD.calculate({ values: c15m, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }).pop() || { MACD: 0, signal: 0 };
                const m4 = MACD.calculate({ values: c4h, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }).pop() || { MACD: 0, signal: 0 };

                // 기존 UI 구조(short, long, total)에 값 매칭
                setStatsData([
                    { label: "15분 RSI", short: "RSI", long: r15.toFixed(2), total: r15 > 70 ? "과매수" : r15 < 30 ? "과매도" : "보통" },
                    { label: "4시간 RSI", short: "RSI", long: r4.toFixed(2), total: r4 > 70 ? "과매수" : r4 < 30 ? "과매도" : "보통" },
                    { label: "15분 MACD", short: "Sig", long: m15.signal.toFixed(2), total: m15.MACD.toFixed(2) },
                    { label: "4시간 MACD", short: "Sig", long: m4.signal.toFixed(2), total: m4.MACD.toFixed(2) },
                ]);
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
        if (walletData && Object.values(walletData).some(value => value > 0)) {
            isExChange = true;
        }

        setIsExChange(isExChange);
    },[walletData])

    // 승엽님 hook
    useEffect(() => {
        if (!isLogin) {
             setPositionData([]);
             setLoadingPositions(false);
             setPositionError(null);
             return; 
        }

        const fetchAndSetPositions = () => {
             // 데이터 로딩 로직 (이전과 동일)
             fetchBingXPositions(API_KEY, API_SECRET)
                .then(result => {
                    if (result.code === 0) {
                        const transformedData = (result.data || []).map(pos => {
                            const unrealizedProfit = parseFloat(pos.unrealizedProfit);
                            const realizedProfit = parseFloat(pos.realisedProfit);
                            const coinSymbol = pos.symbol.split('-')[0];

                            return {
                                coin: coinSymbol, 
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
                        setPositionData(transformedData);
                        setPositionError(null);
                    } else {
                        setPositionError(`API 오류 (Code: ${result.code}): ${result.msg}`);
                    }
                })
                .catch(err => {
                    console.error("Position Fetch Error:", err);
                    setPositionError(`데이터 로드 실패: ${err.message}`);
                })
                .finally(() => {
                    setLoadingPositions(false);
                });
        };

        // 1. 컴포넌트 마운트 시 즉시 한 번 호출
        fetchAndSetPositions();

        // 2. ★ 1초(1000ms)마다 주기적으로 호출하여 업데이트 ★
        const intervalId = setInterval(fetchAndSetPositions, 3000); 

        // 3. 클린업 함수: 컴포넌트가 언마운트되거나 useEffect가 다시 실행될 때 타이머를 해제
        return () => clearInterval(intervalId);

    }, [API_KEY, API_SECRET, isLogin]); // isLogin 상태가 변경될 때만 다시 실행

    // Ref로 호출 제한
    useEffect(() => {
        if (!walletData) return;

        // 중복 호출 방지
        if (prevWalletRef.current &&
            JSON.stringify(prevWalletRef.current) === JSON.stringify(walletData)
        ) return;

        prevWalletRef.current = walletData;

        // walletData에서 직접 가져오기

        const th = walletData.trade_history || {};
        // 거래 내역
        const formatLocalTime = (isoTime) => {
            if (!isoTime) return "N/A";
            const date = new Date(isoTime); // 자동으로 현지 시간 기준
            const year = String(date.getFullYear()).slice(2); // 뒤 두 자리만
            const month = String(date.getMonth() + 1).padStart(2, '0'); // 1~12
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');

            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        };
        setHistoryData([
            { time: formatLocalTime(th?.['BTC']?.created_at), coin: "BTC", type: th?.['BTC']?.side, qty: th?.['BTC']?.executed_volume || 0, isBuy: true },
            { time: formatLocalTime(th?.['ETH']?.created_at), coin: "ETH", type: th?.['ETH']?.side, qty: th?.['ETH']?.executed_volume || 0, isBuy: false },
            { time: formatLocalTime(th?.['XRP']?.created_at), coin: "XRP", type: th?.['XRP']?.side, qty: th?.['XRP']?.executed_volume || 0, isBuy: true },
            { time: formatLocalTime(th?.['BCH']?.created_at), coin: "BCH", type: th?.['BCH']?.side, qty: th?.['BCH']?.executed_volume || 0, isBuy: false },
        ]);

    }, [walletData]);

    const prevPriceRef = useRef({});
    useEffect(() => {
        if (!currentPrice) return;

        const oc = walletData.owner_coin || {};

        // currentPrice 변경 시 ownerValue 계산
        const newOwnerValue = {};
        Object.keys(oc).forEach((coin) => {
            const amount = oc[coin] || 0;
            const price = currentPrice[coin] || 0;
            newOwnerValue[coin] = Math.floor(amount * price);
        });

        prevPriceRef.current = currentPrice;

        // 순서를 지정한 배열
        const coinOrder = ["BTC", "ETH", "XRP", "BCH"];

        // holdingData 업데이트
        setHoldingData(
            coinOrder.map((coin) => ({
                coin,
                amount: oc[coin] || 0,
                value: newOwnerValue[coin] || 0,
                isWin: coin === "BTC" || coin === "ETH", // 필요에 따라 변경
            }))
        );
    }, [currentPrice, walletData]);

    // 1. 청산 현황
    const [statsData, setStatsData] = useState([
    { label: "15분 RSI", short: "로딩중", long: "로딩중", total: "로딩중" },
    { label: "4시간 RSI", short: "로딩중", long: "로딩중", total: "로딩중" },
    { label: "15분 MACD", short: "로딩중", long: "로딩중", total: "로딩중" },
    { label: "4시간 MACD", short: "로딩중", long: "로딩중", total: "로딩중" },
]);



    const styles = {
        container: {
            width: '100%',
            height: '100%',
            display: 'flex',
            gap: '10px',
        },
        cardsArea: {
            flex: 0.7, 
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '10px',
        },
        rightArea: {
            flex: 1.3, 
            display: 'flex',
            gap: '10px',
        },
        
        // 박스 공통 스타일
        card: {
            backgroundColor: 'var(--trade-card-bg)',
            border: '1px solid var(--trade-border)', 
            borderRadius: '4px',
            padding: '10px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            fontSize: '0.8rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
        },
        historyBox: {
            flex: 1,
            backgroundColor: 'var(--trade-card-bg)',
            border: '1px solid var(--trade-border)', 
            borderRadius: '4px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },

        // --- 텍스트 스타일 ---
        title: {
            fontSize: '0.9rem',
            color: 'var(--trade-text)', 
            marginBottom: '8px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
        },
        row_long: {
            fontSize: '0.8rem',
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '5px',
            backgroundColor: 'var(--trade-bg)', 
            padding: '6px 10px',
            borderRadius: '2px',
            alignItems: 'center',
        },
        row_short: {
            fontSize: '0.8rem',
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '5px',
            backgroundColor: 'var(--trade-bg)', 
            padding: '6px 10px',
            borderRadius: '2px',
            alignItems: 'center',
        },
        row_total: {
            fontSize: '0.85rem',
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '2px',
            marginTop: '5px',
            color: 'var(--trade-subtext)', 
        },
        shortText: { color: '#f23645', fontWeight: 'bold' }, 
        longText: { color: '#089981', fontWeight: 'bold' },  
        totalText: { fontSize: '1rem', fontWeight: 'bold', color: 'var(--trade-text)' }, 

        // --- 테이블 헤더 ---
        sectionHeader: {
            padding: '8px 10px',
            fontSize: '0.8rem',
            fontWeight: 'bold',
            borderBottom: '1px solid var(--trade-border)',
            backgroundColor: 'var(--trade-card-bg)',
            color: 'var(--trade-text)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
        },
        
        // 포지션 헤더
        posHeader: {
            display: 'grid',            
            // 코인 | Side | 진입가 | 수량 | 미실현 | 실현 | 청산가
            gridTemplateColumns: '0.7fr 0.6fr 1fr 0.8fr 1fr 1fr 1fr',  
            padding: '6px 0', fontSize: '0.65rem', fontWeight: 'bold',
            backgroundColor: 'var(--trade-bg)', borderBottom: '1px solid var(--trade-border)',
            color: 'var(--trade-subtext)', textAlign: 'center', 
        },
        // 보유코인 헤더
        holdHeader: {
            display: 'grid',
            gridTemplateColumns: '0.9fr 0.9fr 1.2fr', 
            padding: '6px 0', fontSize: '0.65rem', fontWeight: 'bold',
            backgroundColor: 'var(--trade-bg)', borderBottom: '1px solid var(--trade-border)',
            color: 'var(--trade-subtext)', textAlign: 'center', 
        },
        // ★ 거래내역 헤더 (6개 컬럼으로 변경) => 5개 컬럼으로
        histHeader: {
            display: 'grid',
            // 시간 | 코인 | 종류 | 수량
            gridTemplateColumns: '2fr 1fr 1fr 1.5fr', 
            padding: '6px 0', fontSize: '0.65rem', fontWeight: 'bold',
            backgroundColor: 'var(--trade-bg)', borderBottom: '1px solid var(--trade-border)',
            color: 'var(--trade-subtext)', textAlign: 'center', 
        },

        tableRow: {
            display: 'grid',
            padding: '4px 0',
            fontSize: '0.7rem',
            borderBottom: '1px solid var(--trade-border)',
            alignItems: 'center',
            transition: 'background-color 0.2s',
            cursor: 'default',
            textAlign: 'center',
        },
        
        coinWrapper: {
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '3px', fontWeight: 'bold',
        },
        coinIcon: { width: '12px', height: '12px', borderRadius: '50%' },
        
        // 배지 스타일
        badgeLong: {
            backgroundColor: 'rgba(8, 153, 129, 0.15)', color: '#089981',
            padding: '1px 3px', borderRadius: '2px', fontSize: '0.65rem', fontWeight: 'bold'
        },
        badgeShort: {
            backgroundColor: 'rgba(242, 54, 69, 0.15)', color: '#f23645',
            padding: '1px 3px', borderRadius: '2px', fontSize: '0.65rem', fontWeight: 'bold'
        },
        // ★ 구분(선물/현물) 배지 스타일
        badgeSpot: {
            backgroundColor: 'rgba(41, 98, 255, 0.1)', color: '#2962ff',
            padding: '1px 3px', borderRadius: '2px', fontSize: '0.65rem', fontWeight: 'bold'
        },
        badgeFuture: {
            backgroundColor: 'rgba(255, 152, 0, 0.1)', color: '#ff9800',
            padding: '1px 3px', borderRadius: '2px', fontSize: '0.65rem', fontWeight: 'bold'
        },

        pnlWin: { color: '#089981', fontWeight: 'bold' },
        pnlLose: { color: '#f23645', fontWeight: 'bold' },
    };

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
                    <div style={{textAlign:'center', padding:'20px', color:'var(--trade-subtext)'}}>포지션 데이터를 불러오는 중...</div>
                )}

                {!loadingPositions && positionError && (
                    <div style={{textAlign:'center', padding:'20px', color:'#f23645', wordBreak:'break-all'}}>
                        API 오류: {positionError}
                    </div>
                )}

                {!loadingPositions && !positionError && positionData.length === 0 && (
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
                        <span style={{color:'var(--trade-subtext)'}}>$ {pos.entry}</span>
                        <span style={{color:'var(--trade-text)'}}>{pos.amount}</span>
                        <span style={pos.isWin ? styles.pnlWin : styles.pnlLose}>{pos.pnl}</span>
                        <span style={pos.isRealizedWin ? styles.pnlWin : styles.pnlLose}>{pos.realizedPnl}</span> 
                        <span style={{color:'var(--trade-subtext)'}}>$ {pos.liquidationPrice}</span> 
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
                            <div
                                key={i}
                                style={{ ...styles.tableRow, gridTemplateColumns: '0.9fr 0.9fr 1.2fr' }}
                            >
                                <div style={styles.coinWrapper}>
                                    <img src={coinIcons[hold.coin]} alt="" style={styles.coinIcon} />
                                    <span>{hold.coin}</span>
                                </div>

                                <span style={{ color: 'var(--trade-text)' }}>{hold.amount}</span>

                                <div
                                    className="won"
                                    style={{
                                        fontWeight: 'bold',
                                        display: 'flex',
                                        flexDirection: 'row',
                                        justifyContent: 'space-between',
                                        paddingRight: '30px',
                                        paddingLeft: '30px',
                                    }}
                                >
                                    <div>{Number(hold.value).toLocaleString()}</div>
                                    <div>₩</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <div
                    style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--text-color)',
                        fontSize: '1em',
                    }}
                >
                    Information에서 거래소를 설정해 주세요.
                </div>
            )}
        </div>
    );

    // [3] 거래 내역 (★ 구분 컬럼 추가됨)
    const renderHistoryTable = () => (
        <div style={styles.historyBox}>
            <div style={styles.sectionHeader}>
                <span>📋 거래 내역</span>
            </div>           
            {isexchange ? (             
                <>
            <div style={styles.histHeader}>
                <span>시간</span>
                <span>코인</span>
                <span>타입</span> {/* 추가됨 */}
                <span>수량</span>
            </div>
         
            <div style={{overflowY:'auto', flex:1}} className="custom-scroll">
                {historyData.map((trade, i) => (
                    <div key={i} style={
                        {...styles.tableRow, 
                        gridTemplateColumns: '2fr 1fr 1fr 1.5fr'}}>
                        <span style={{color:'var(--trade-subtext)'}}>{trade.time}</span>

                        <div style={styles.coinWrapper}>
                            <img src={coinIcons[trade.coin]} alt="" style={styles.coinIcon} />
                            <span>{trade.coin}</span>
                        </div>

                        {/* <span style={{color:'var(--trade-subtext)'}}>{trade.market}</span>
                        */}
                        {/* ★ 구분 컬럼 (현물/선물) */}
                        {/* <div>
                            <span style={trade.category === '선물' ? styles.badgeFuture : styles.badgeSpot}>
                                {trade.category}
                            </span>
                        </div>
                        */}

                        <div>
                            <span style={
                                trade.type == "bid" ? 
                                styles.badgeLong : styles.badgeShort}>{trade.type}
                            </span>
                        </div>
                        
                        <span style={{color:'var(--trade-subtext)'}}>{trade.qty}</span>
                    </div>
                ))}
            </div>
            </>
                        ): (
                <div
                    style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--text-color)',
                        fontSize: '1em',
                    }}
                >
                    Information에서 거래소를 설정해 주세요.
                </div>
            )}
        </div>
    );

    return (
        <div style={styles.container}>
            {/* 좌측: 청산 현황 */}
            <div style={styles.cardsArea}>
                {statsData.map((stat, idx) => (
                    <div key={idx} style={styles.card}>
                        <div style={styles.title}>⚡ {stat.label}</div>
                        <div style={styles.row_long}>
                            <span style={{color:'var(--trade-subtext)'}}>지표값</span>
                            <span style={styles.longText}>${stat.long}</span>
                        </div>
                        {/* <div style={styles.row_short}>
                            <span style={{color:'var(--trade-subtext)'}}>숏 청산</span>
                            <span style={styles.shortText}>${stat.short}</span>
                        </div> */}
                        <div style={styles.row_total}>
                            <span>현재 상태</span>
                        </div>
                        <div style={{textAlign:'center'}}>
                            <span style={styles.totalText}>{stat.total}</span>
                        </div>
                    </div>
                ))}
            </div>
            
            {/* 우측: 포지션 - 보유코인 - 거래내역 */}
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
                        <p style={{margin:0, fontSize:'0.8rem', color:'var(--trade-subtext)'}}>
                            개인정보 (ex 투자성향, 즐겨찾기, 자금 등)
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}