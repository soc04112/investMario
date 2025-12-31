// src/components/dashboard/ProfileModal.jsx

import React, { useState } from 'react';
import '../../styles/dashboard/ProfileModal.css';

export default function ProfileModal({ onClose }) {
    const [activeTab, setActiveTab] = useState('wallet');

    // API Key 입력을 위한 상태 관리
    const [apiKeys, setApiKeys] = useState({
        upbit: { access: '', secret: '' },
        bithumb: { access: '', secret: '' },
        bingx: { access: '', secret: '' },
    });

    // 입력 핸들러
    const handleApiKeyChange = (exchange, type, value) => {
        setApiKeys(prev => ({
            ...prev,
            [exchange]: {
                ...prev[exchange],
                [type]: value
            }
        }));
    };

    const handleSaveApiKeys = async () => {
        // 1. 빈 값은 제외하고 입력된 키만 추려서 전송
        const cleanData = {};
        console.log("1", cleanData);
        // Upbit
        if (apiKeys.upbit.access) cleanData.upbit_access_key = apiKeys.upbit.access;
        if (apiKeys.upbit.secret) cleanData.upbit_secret_key = apiKeys.upbit.secret;
        
        // Bithumb
        if (apiKeys.bithumb.access) cleanData.bithumb_access_key = apiKeys.bithumb.access;
        if (apiKeys.bithumb.secret) cleanData.bithumb_secret_key = apiKeys.bithumb.secret;
        
        // BingX
        if (apiKeys.bingx.access) cleanData.bingx_access_key = apiKeys.bingx.access;
        if (apiKeys.bingx.secret) cleanData.bingx_secret_key = apiKeys.bingx.secret;
        console.log("2", cleanData);

        const payload = { data: cleanData };
        console.log("Payload to send:", payload);

        try {
            const response = await fetch('/api/userinfo_modify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            console.log("Response status:", response.status);
            console.log("Response headers:", response.headers);
            console.log("Response ok:", response.ok);

            const result = await response.json();

            console.log("Response data:", result);
        

            if (response.ok && result.data === "Update success") {
                alert("API 키가 안전하게 저장되었습니다.");
                // 저장 후 입력창 초기화가 필요하다면 아래 주석 해제
                // setApiKeys({ upbit: { access: '', secret: '' }, ... });
            } else {
                alert("저장에 실패했습니다. 다시 시도해주세요.");
                console.error("Save failed:", result);
            }
        } catch (error) {
            console.error("API Key Save Error:", error);
            alert("서버 통신 중 오류가 발생했습니다.");
        }
    };

    const renderContent = () => {
        switch (activeTab) {
            // case 'profile':
            //     return (
            //         <>
            //             <h2 className="content-title">내 프로필</h2>
            //             <div className="profile-card">
            //                 <div className="profile-avatar">
            //                     <i className="fa-solid fa-user"></i>
            //                 </div>
            //                 <div className="profile-info">
            //                     <h3>MASTER <span className="badge-master">MASTER</span></h3>
            //                     <p>가입일: 2025-01-01</p>
            //                 </div>
            //             </div>

            //             <div className="info-grid">
            //                 <div className="info-box">
            //                     <span className="info-label">이메일</span>
            //                     <span className="info-value">master@investmario.com</span>
            //                 </div>
            //                 <div className="info-box">
            //                     <span className="info-label">휴대폰 번호</span>
            //                     <span className="info-value">010-1234-5678</span>
            //                 </div>
            //                 <div className="info-box">
            //                     <span className="info-label">투자 성향</span>
            //                     <span className="info-value" style={{color:'#f23645'}}>공격투자형 (Aggressive)</span>
            //                 </div>
            //                 <div className="info-box">
            //                     <span className="info-label">총 자산</span>
            //                     <span className="info-value">$10,000.00</span>
            //                 </div>
            //             </div>
            //         </>
            //     );
            
            case 'wallet':
                return (
                    <>
                        <h2 className="content-title">계좌 정보 (API 연동)</h2>
                        <div className="scroll-container">
                            {['upbit', 'bithumb', 'bingx'].map((exchange) => (
                                <div key={exchange} className="info-box">
                                    <h3 className="exchange-title">
                                        {exchange} Exchange
                                    </h3>
                                    
                                    <div className="form-group">
                                        <label className="form-label">Access Key</label>
                                        <input 
                                            type="text" 
                                            className="form-input"
                                            value={apiKeys[exchange].access}
                                            onChange={(e) => handleApiKeyChange(exchange, 'access', e.target.value)}
                                            placeholder="Enter Access Key"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Secret Key</label>
                                        <input 
                                            type="password" 
                                            className="form-input"
                                            value={apiKeys[exchange].secret}
                                            onChange={(e) => handleApiKeyChange(exchange, 'secret', e.target.value)}
                                            placeholder="Enter Secret Key"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button className="primary-btn" onClick={handleSaveApiKeys}>
                            API 키 저장하기
                        </button>
                    </>
                );

            case 'security':
                return (
                    <>
                        <h2 className="content-title">보안 설정</h2>
                        <div className="info-box" style={{marginBottom:'15px'}}>
                            <span className="info-label">비밀번호</span>
                            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                <span className="info-value">********</span>
                                <button style={{background:'#2962ff', color:'white', border:'none', padding:'6px 12px', borderRadius:'4px', cursor:'pointer', fontSize:'0.85rem'}}>변경</button>
                            </div>
                        </div>
                        <div className="info-box">
                            <span className="info-label">2단계 인증 (2FA)</span>
                            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                <span className="info-value" style={{color:'#089981'}}>사용 중 (Google OTP)</span>
                                <button style={{background:'transparent', border:'1px solid #444', color:'var(--trade-text)', padding:'6px 12px', borderRadius:'4px', cursor:'pointer', fontSize:'0.85rem'}}>설정</button>
                            </div>
                        </div>
                    </>
                );
            default:
                return <div>준비 중인 기능입니다.</div>;
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                
                {/* 좌측 사이드바 */}
                <div className="modal-sidebar">
                    {/* <div 
                        className={`sidebar-item ${activeTab === 'profile' ? 'active' : ''}`}
                        onClick={() => setActiveTab('profile')}
                    >
                        <i className="fa-solid fa-user"></i> 기본 정보
                    </div> */}
                    <div 
                        className={`sidebar-item ${activeTab === 'wallet' ? 'active' : ''}`}
                        onClick={() => setActiveTab('wallet')}
                    >
                        <i className="fa-solid fa-wallet"></i> 계좌 정보
                    </div>
                    <div 
                        className={`sidebar-item ${activeTab === 'security' ? 'active' : ''}`}
                        onClick={() => setActiveTab('security')}
                    >
                        <i className="fa-solid fa-shield-halved"></i> 보안 설정
                    </div>
                    {/* <div 
                        className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
                        onClick={() => setActiveTab('settings')}
                    >
                        <i className="fa-solid fa-gear"></i> 환경 설정
                    </div> */}
                </div>

                {/* 우측 콘텐츠 */}
                <div className="modal-content">
                    <button className="close-btn" onClick={onClose}>
                        <i className="fa-solid fa-xmark"></i>
                    </button>
                    {renderContent()}
                </div>
            </div>
        </div>
    );
}