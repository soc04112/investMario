// src/components/common/Header.jsx

import "../../styles/common/Header.css";
import GoogleLogin from '../GoogleLogin/GoogleLogin.jsx';
import ProfileModal from '../dashboard/ProfileModal.jsx';
import { useState, useEffect } from 'react';

export default function Header({ darkMode, setDarkMode, isLogin, verify, Username, user_information, wallet_data}) {

    const [showProfileModal, setShowProfileModal] = useState(false);
    
    // [1] 레버리지 상태 (DB 대신 로컬 스토리지 사용)
    const [leverage, setLeverage] = useState(() => {
        // 화면 로드 시 저장된 값이 있으면 가져오고, 없으면 10으로 초기화
        const saved = localStorage.getItem('user_leverage');
        return saved ? parseInt(saved, 10) : 10;
    });
    const [showLev, setShowLev] = useState(false); 

    // [2] 코인 거래 성향 상태
    // 초기값을 "미설정"으로 변경하여 클릭 가능하도록 함
    const [tendency, setTendency] = useState("미설정");
    const [showTendency, setShowTendency] = useState(false);

    // [3] 자금 및 등급 상태
    const [capital, setCapital] = useState(0);
    const [tier, setTier] = useState("Demo");

    // [4] 팝업 관련 상태
    const [showConfirm, setShowConfirm] = useState(false); 
    const [confirmType, setConfirmType] = useState(null);  
    const [pendingValue, setPendingValue] = useState(null); 

    // 유저 정보(등급, 자금, 성향) 가져오기 - DB 연동
    useEffect(() => {
        if (verify === "verified") {
            const fetchUserData = async () => {
                try {
                    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    const response = await fetch('/api/get_user', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ timezone: timezone })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        
                        // 등급, 자금, 성향은 DB 데이터 사용
                        if (data) {
                            // DB 값이 있으면 설정, 없으면 "미설정" 유지
                            setTendency(data.play || "미설정");
                        }
                    }
                } catch (error) {
                    console.error("Failed to fetch user data:", error);
                }
            };
            fetchUserData();
        }
    }, [verify]);

    useEffect(() => {
        if (wallet_data?.available_cash == null) return
        setCapital(wallet_data.available_cash)
    }, [wallet_data?.available_cash])

    useEffect(() => {
        setTier(user_information.tier)
    }, [user_information])

    // 성향별 색상 매핑
    const getTendencyColor = (t) => {
        if (t === "공격형") return "text-red";
        if (t === "안전형") return "text-green";
        if (t === "미설정") return ""; // 미설정은 기본 색상 (흰색/회색)
        return "text-yellow"; 
    };

    // DB 정보 업데이트 함수
    const updateUserInfo = async (dataObj) => {
        try {
            await fetch('/api/userinfo_modify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: dataObj
                })
            });
        } catch (error) {
            console.error("Failed to save user info:", error);
        }
    };

    // 자동매매 실행 조건 검사 함수
    const validateSettings = () => {
        if (!user_information) {
             alert("사용자 정보를 불러오는 중입니다. 잠시 후 다시 시도해주세요.");
             return false;
        }

        const { exchange, usemodel, gpt_key, grok_key, upbit_key, bingx_key } = user_information;

        if (!exchange || exchange === "없음") {
            alert("자동매매를 시작하려면 먼저 '내 정보'에서 거래소를 선택해주세요.");
            return false;
        }

        if (!usemodel || usemodel === "없음") {
            alert("자동매매를 시작하려면 먼저 '내 정보'에서 AI 모델을 선택해주세요.");
            return false;
        }

        if (usemodel.startsWith("GPT") && !gpt_key) {
            alert("GPT API Key가 설정되지 않았습니다. API 설정을 확인해주세요.");
            return false;
        }
        if (usemodel.startsWith("Grok") && !grok_key) {
            alert("Grok API Key가 설정되지 않았습니다. API 설정을 확인해주세요.");
            return false;
        }

        if (exchange === "Upbit" && !upbit_key) {
            alert("Upbit API Key가 설정되지 않았습니다. API 설정을 확인해주세요.");
            return false;
        }
        if (exchange === "BingX" && !bingx_key) {
            alert("BingX API Key가 설정되지 않았습니다. API 설정을 확인해주세요.");
            return false;
        }

        return true;
    };

    // ★ 확인 팝업 - '예' 클릭 시 실행
    const handleConfirmYes = async () => {
        if (confirmType === 'leverage') {
            setShowLev(false);
            localStorage.setItem('user_leverage', leverage);
            console.log("Leverage saved locally:", leverage);
            setShowConfirm(false);

        } else if (confirmType === 'tendency') {
            // [수정] "미설정"으로 되돌리는 경우가 아니라면 유효성 검사 수행
            if (pendingValue !== "미설정" && !validateSettings()) {
                setShowConfirm(false);
                return;
            }

            setTendency(pendingValue);
            setShowTendency(false);
            setShowConfirm(false); 
            
            // 성향에 따른 프롬프트 자동 설정
            let newPrompt = "";
            if (pendingValue === "공격형") {
                newPrompt = "공격적으로 투자해줘";
            } else if (pendingValue === "중립형") {
                newPrompt = "중립적으로 투자해줘";
            } else if (pendingValue === "안전형") {
                newPrompt = "안전적으로 투자해줘";
            } else if (pendingValue === "미설정") {
                newPrompt = ""; // 프롬프트 초기화
            }

            // DB 저장
            await updateUserInfo({ 
                play: pendingValue === "미설정" ? "" : pendingValue, // 미설정이면 빈 값 저장
                user_prompt: newPrompt
            });

            window.location.reload();
        }
    };

    const handleConfirmNo = () => {
        if (confirmType === 'leverage') {
            const saved = localStorage.getItem('user_leverage');
            setLeverage(saved ? parseInt(saved, 10) : 10);
        }
        setShowConfirm(false);
    };

    const handleLoginSuccess = (response) => {
        console.log("Google Login Success:", response);
        localStorage.setItem("isLogin", "true");
        window.location.reload();
    };

    const handleLogout = async () => {
        const res = await fetch(`${import.meta.env.VITE_POST_URL}/api/logout`, {
        method: "POST",
        credentials: "include",
        });

        const data = await res.json();
        if (data.message == "")
        navigate("/trade");
        window.location.reload();
    };

    return (
        <div className="custom-header-content">
            <div className="mario-logo">
                <span className="text-red">투자</span>
                <div className="mario-icon-placeholder">M</div>
                <span className="text-blue">마리오</span>
            </div>

            <div className="header-spacer"></div>

            <div className="header-utils">
            {verify === null ? (
                <div className="loading">로딩 중...</div>
            ) : verify === "verified" ? (
                <>
                <div className="user-info-bar">
                    <div className="info-item">
                        <span className="label">지갑 여유 자금:</span>
                        <span className="value">{capital.toLocaleString()} 원</span>
                    </div>
                    {/* [1] 포지션 성향 (레버리지) */}
                    <div className="info-item" style={{ position: 'relative' }}>
                        <span className="label">포지션 성향:</span>
                        <button
                            className="leverage-btn"
                            onClick={() => {
                            setShowLev(!showLev);
                            setShowTendency(false);
                            }}
                        >
                            {leverage}x
                        </button>
                        {showLev && (
                            <div className="leverage-popup">
                                <div className="lev-header">
                                    <span>Leverage</span>
                                    <span className="lev-val">{leverage}x</span>
                                </div>
                                <input
                                    type="range"
                                    min="1"
                                    max="100"
                                    step="1"
                                    value={leverage}
                                    onChange={(e) => setLeverage(e.target.value)}
                                    className="lev-slider"
                                />
                                <div className="lev-marks">
                                    <span>1x</span>
                                    <span>50x</span>
                                    <span>100x</span>
                                </div>
                                <div
                                    className="popup-confirm-btn"
                                    onClick={() => {
                                    setConfirmType('leverage');
                                    setShowConfirm(true);
                                    }}
                                >
                                    확인
                                </div>
                            </div>
                        )}
                    </div>

                    {/* [2] 코인 거래 성향 */}
                    <div className="info-item" style={{ position: 'relative' }}>
                    <span className="label">코인 거래 성향:</span>
                    <button
                        className={`tendency-btn ${getTendencyColor(tendency)}`}
                        onClick={() => {
                            // 클릭 방지 로직 제거
                            setShowTendency(!showTendency);
                            setShowLev(false);
                        }}
                        style={{ minWidth: '60px' }}
                    >
                        {tendency}
                    </button>

                    {showTendency && (
                        <div className="tendency-popup">
                        {/* [수정] 옵션에 "미설정" 추가 */}
                        {["미설정", "공격형", "중립형", "안전형"].map((type) => (
                            <div
                            key={type}
                            className={`tendency-option ${tendency === type ? 'active' : ''}`}
                            onClick={() => {
                                setPendingValue(type);
                                setConfirmType('tendency');
                                setShowConfirm(true);
                            }}
                            >
                            {type}
                            </div>
                        ))}
                        </div>
                    )}
                    </div>

                    <div className="info-item">
                        <span className="label">등급:</span>
                        <span className="value badge-master">{tier}</span>
                    </div>

                    <span className="user-name"><strong>{Username}</strong>님</span>
                </div>

                <div className="divider"></div>

                <button className="icon-btn" title="내 정보 상세" onClick={() => setShowProfileModal(true)}>
                    <i className="fa-solid fa-user-gear"></i>
                </button>

                <button
                    className="icon-btn"
                    onClick={() => setDarkMode(prev => !prev)}
                    title="다크모드 토글"
                >
                    {darkMode ? '☀️' : '🌙'}
                </button>

                <button className="logout-btn" onClick={handleLogout}>
                    로그아웃
                </button>
                </>
            ) : (
                <>
                <button
                    className="icon-btn"
                    onClick={() => setDarkMode(prev => !prev)}
                    title="다크모드 토글"
                >
                    {darkMode ? '☀️' : '🌙'}
                </button>

                <div className="login-btn-wrapper">
                    <GoogleLogin onLoginSuccess={handleLoginSuccess} />
                </div>
                </>
            )}
            </div>

            {showProfileModal && (
                <ProfileModal onClose={() => setShowProfileModal(false)} user_information={user_information}/>
            )}

            {showConfirm && (
                <div className="confirm-overlay">
                    <div className="confirm-box">
                        <p className="confirm-msg">설정을 변경하시겠습니까?</p>
                        <div className="confirm-btns">
                            <button className="btn-yes" onClick={handleConfirmYes}>예</button>
                            <button className="btn-no" onClick={handleConfirmNo}>아니오</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}