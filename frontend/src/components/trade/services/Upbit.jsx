import { useEffect, useRef, useState } from "react";

export default function useUpbitPrice() {
    const [currentPrice, setCurrentPrice] = useState({});
    const wsRef = useRef(null);
    const priceBuffer = useRef({});      // WebSocket 이벤트 임시 저장
    const updateTimer = useRef(null);    // 상태 갱신용 타이머

    const coins = ['BTC', 'ETH', 'SOL', 'XRP', 'BCH'];

    useEffect(() => {
        const ws = new WebSocket("wss://api.upbit.com/websocket/v1");
        wsRef.current = ws;

        ws.onopen = () => {
            const subscribeMsg = [
                { ticket: "wallet-price" },
                {
                    type: "ticker",
                    codes: coins.map(c => `KRW-${c}`),
                    isOnlyRealtime: true
                }
            ];
            ws.send(JSON.stringify(subscribeMsg));
        };

        ws.onmessage = async (event) => {
            try {
                const text = await event.data.text();
                let data = JSON.parse(text);
                if (!Array.isArray(data)) data = [data];

                data.forEach(item => {
                    if (!item.code || !item.trade_price) return;
                    const coinCode = item.code.replace("KRW-", "");
                    priceBuffer.current[coinCode] = item.trade_price;
                });

                // 타이머가 없으면 1초 후 상태 업데이트
                if (!updateTimer.current) {
                    updateTimer.current = setTimeout(() => {
                        setCurrentPrice({ ...priceBuffer.current });
                        updateTimer.current = null;
                    }, 1000); // 1초
                }

            } catch (err) {
                console.error("WebSocket parsing error:", err);
            }
        };

        return () => {
            if (wsRef.current) wsRef.current.close();
            if (updateTimer.current) clearTimeout(updateTimer.current);
        };
    }, []);

    return currentPrice;
}
