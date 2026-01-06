// src/components/dashboard/UserInfoModify.jsx

import './styles/UserInfoModify.css'
import { useState } from 'react';
// import CountrySelect from './services/countryselect' 
import {User_Infor_Modify} from './services/user_inforamtion'

export default function Userinfo({ form, setForm, activeTab }) {
  // 키별 눈 표시 상태
  const [showKeys, setShowKeys] = useState({
    gpt: false,
    grok: false,

    upbit_secret: false,
    upbit_access: false,

    bingx_secret : false,
    bingx_access : false,
  });

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const updateTicker = (coin) => setForm(prev => ({
    ...prev,
    ticker: { ...prev.ticker, [coin]: !prev.ticker[coin] },
  }));

  const toggleShowKey = (key) => setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));

  // 현재 선택된 Model/Exchange에 따라 활성화 상태(ON/OFF) 결정
  const isGptActive = form.usemodel && form.usemodel.includes("GPT");
  const isGrokActive = form.usemodel && form.usemodel.includes("Grok");
  
  // [수정] 현물 활성화: 업비트 선택 시
  const isUpbitActive = form.exchange === "Upbit";
  
  // [수정] 선물 활성화: BingX 키가 모두 입력되어 있으면 ON
  const isBingxActive = form.bingx_access_key && form.bingx_access_key.length > 0 && 
                        form.bingx_secret_key && form.bingx_secret_key.length > 0;

  // 그룹별 키 정의
  const aiKeys = [
    { label: "GPT", value: form.gpt_key_value, status: isGptActive, keyName: "gpt", formField: "gpt_key_value" },
    { label: "Grok", value: form.grok_key_value, status: isGrokActive, keyName: "grok", formField: "grok_key_value" },
  ];

  const futureKeys = [
    { label: "Bingx Access", value: form.bingx_access_key, status: isBingxActive, keyName: "bingx_access", formField: "bingx_access_key" },
    { label: "Bingx Secret", value: form.bingx_secret_key, status: isBingxActive, keyName: "bingx_secret", formField: "bingx_secret_key" },
  ];

  const spotKeys = [
    { label: "Upbit Access", value: form.upbit_access_key, status: isUpbitActive, keyName: "upbit_access", formField: "upbit_access_key" },
    { label: "Upbit Secret", value: form.upbit_secret_key, status: isUpbitActive, keyName: "upbit_secret", formField: "upbit_secret_key" },
  ];

  // 키 입력 폼 렌더링 헬퍼 함수
  const renderKeyGroup = (label, keys) => (
    <div className="toggle-group">
      <label>{label}</label>
      <div className="ticker-list">
        {keys.map((k, idx) => (
          <div key={idx} className='ticker-form'>
            <button className={`key-toggle ${k.status ? "on" : ""}`}>
              {k.label} {k.status ? "ON" : "OFF"}
            </button>
            <div className='key-form'>
              <input
                type={showKeys[k.keyName] ? "text" : "password"}
                value={k.value || ""}
                onChange={(e) => update(k.formField, e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px 36px 10px 10px",
                  borderRadius: "6px",
                  border: "1px solid #ccc",
                  backgroundColor: "var(--bg-color)",
                  fontSize: "0.9rem",
                  boxSizing: "border-box"
                }}
              />
              <button
                onClick={() => toggleShowKey(k.keyName)}
                style={{
                  position: "absolute",
                  right: "10px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  padding: 0,
                }}
              >
                {showKeys[k.keyName] ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#4a76e8" viewBox="0 0 24 24">
                    <path d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
                    <circle cx="12" cy="12" r="2.5"/>
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#aaa" viewBox="0 0 24 24">
                    <path d="M12 5c-7 0-11 7-11 7s4 7 11 7c1.7 0 3.28-.35 4.7-.97l1.62 1.62 1.41-1.41-1.5-1.5c2.05-1.53 3.38-3.54 3.38-3.54s-4-7-11-7zm0 12c-2.76 0-5-2.24-5-5 0-.54.1-1.06.28-1.54l6.26 6.26c-.48.18-1 .28-1.54.28z"/>
                    <path d="M0 0h24v24H0z" fill="none"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const validateFormForRun = () => {
    // [수정] 현물 또는 선물 중 하나라도 활성화되면 OK
    // (Upbit가 선택되었거나, BingX 키가 존재하거나)
    const hasSpot = form.exchange && form.exchange !== "없음";
    const hasFuture = form.bingx_access_key && form.bingx_secret_key;

    if (!hasSpot && !hasFuture) {
      alert("봇을 실행하려면 현물 거래소(Upbit)를 선택하거나 선물 거래소(BingX) API 키를 입력해주세요.");
      return false;
    }

    // model
    if (!form.usemodel || form.usemodel === "없음") {
      alert("봇을 실행하려면 모델을 선택해주세요.");
      return false;
    }

    // model key
    if (form.usemodel.startsWith("GPT")) {
      if (!form.gpt_key_value) {
        alert("실행을 위해 GPT API Key를 입력해주세요.");
        return false;
      }
    }
    if (form.usemodel.startsWith("Grok")) {
        if (!form.grok_key_value) {
          alert("실행을 위해 Grok API Key를 입력해주세요.");
          return false;
        }
    }

    // exchange key (Upbit)
    if (form.exchange === "Upbit") {
      if (!form.upbit_access_key || !form.upbit_secret_key) {
        alert("실행을 위해 Upbit Access / Secret Key를 모두 입력해주세요.");
        return false;
      }
    }

    return true;
  };

  const handlePlayToggle = () => {
    if (form.play) {
      update("play", false);
      return;
    }

    if (!validateFormForRun()) return;

    update("play", true);
  };

  return (
    <div className="user">
      <div className="user-information">
        
        {/* 현물 거래 설정 */}
        {activeTab === 'wallet' && (
          <>
            <h2>현물 거래 설정</h2>

            {/* Use Model */}
            <div className="toggle-group">
              <label>모델 선택</label>
              <div className="ticker-list">
                {[
                  { key: "없음", label: "없음" },
                  { key: "GPT_5.0_mini", label: "GPT-5-mini" },
                  { key: "Grok_3.0_mini", label: "Grok-3.0-mini" },
                ].map(({ key, label }) => (
                  <button
                    key={key}
                    type="button"
                    className={`toggle-btn ${form.usemodel === key ? "on" : ""}`}
                    onClick={() => update("usemodel", key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Interval */}
            <div className="toggle-group">
              <label>실행 간격 (초)</label>
              <div className="ticker-list">
                {[14400, 86400].map((sec) => (
                  <button
                    key={sec}
                    type="button"
                    className={`toggle-btn ${form.interval === sec ? "on" : ""}`}
                    onClick={() => update("interval", sec)}
                  >
                    {sec}
                  </button>
                ))}
              </div>
            </div>

            {/* Exchange */}
            <div className="toggle-group">
              <label>거래소 선택</label>
              <div className="ticker-list">
                {[
                  "없음", 
                  // "Bithumb", 
                  "Upbit"].map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    className={`toggle-btn ${form.exchange === ex ? "on" : ""}`}
                    onClick={() => update("exchange", ex)}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>

            {/* Trading Fee */}
            <div className="form-group">
              <label>거래 수수료</label>
              <div className="input-with-unit">
                <input
                  type="text"
                  placeholder="0.1"
                  value={form.trading_fee}
                  onChange={(e) => update("trading_fee", e.target.value)}
                />
                <span>%</span>
              </div>
            </div>

            {/* Ticker toggles */}
            <div className="toggle-group">
              <label>거래 코인 선택</label>
              <div className="ticker-list">
                {Object.keys(form.ticker).map((coin) => (
                  <button
                    key={coin}
                    className={`toggle-btn ${form.ticker[coin] ? "on" : ""}`}
                    onClick={() => updateTicker(coin)}
                  >
                    {coin}
                  </button>
                ))}
              </div>
            </div>

             {/* User Prompt */}
             <h2>프롬프트 설정</h2>
             
             <div style={{ marginBottom: '8px', textAlign: 'right' }}>
                <a 
                  href="https://qqqqaqaqaqq.github.io/bot_trader_backtesting/"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ 
                    fontSize: '0.9rem', 
                    color: '#2962ff', 
                    textDecoration: 'none', 
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  프롬프트 입력 가이드 보기 &#8594;
                </a>
             </div>

              <textarea
                className="user-prompt"
                value={form.user_prompt}
                placeholder="프롬프트를 입력하세요&#10;&#10;ex)&#10;1. 공격적으로 투자해줘&#10;2. 손실 3% 이상 발생 시 부분 매도해줘&#10;3. 수익 5% 이상 발생 시 부분 매도해줘"
                onChange={(e) => {
                  const input = e.target.value;
                  if (input.length > 2000) {
                    alert("최대 2000자까지 입력 가능합니다.");
                    return;
                  }
                  update("user_prompt", input);
                }}
              />
          </>
        )}

        {/* API 설정 */}
        {activeTab === 'api' && (
          <>
            <h2>API 설정</h2>
            {renderKeyGroup("AI", aiKeys)}
            {renderKeyGroup("현물", spotKeys)}
            {/* BingX 키 입력 시 자동으로 ON 표시됨 */}
            {renderKeyGroup("선물", futureKeys)}
          </>
        )}
      </div>

      {/* 버튼 영역 */}
      <div className="toggle-group">
        {activeTab === 'wallet' && (
          <button 
              className={`toggle-btn ${form.play ? "on" : ""}`}
              onClick={handlePlayToggle}
              style={{ width: "100%", marginBottom: "15px" }}
            >
              {form.play ? "자동매매 동작 중" : "자동매매 시작"}
          </button>
        )}

        {/* 저장 버튼: 개인 설정 이외의 탭에서만 노출 */}
        {activeTab !== 'personal' && (
            <button 
            className="save-btn" 
            onClick={() => {
            User_Infor_Modify(form);
            }}>
            저장
            </button>
        )}
      </div>
    </div>
  );
}