// src/components/dashboard/ProfileModal.jsx

import React, { useEffect, useState } from 'react';
import '../../styles/dashboard/ProfileModal.css';

import Userinfo from './UserInfoModify'
import CountrySelect from './services/countryselect'

export default function ProfileModal({ onClose, user_information }) {
    const [form, setForm] = useState({
        username: "",
        usemodel: "없음",

        email: "",

        country: "",
        interval: 14400,

        exchange: "없음",
        play: false,
        
        tier: "Master",     
        tier_time: 365,  
        trading_fee : 0.0,

        ticker: {
            "없음": true,
            BTC: false,
            ETH: false,
            BCH: false,
            XRP: false,
        },
  
        user_prompt: "",

        gpt_key: false,
        grok_key: false,
        // gemini_key: false,
        upbit_key: false,
        bingx_key : false,

        gpt_key_value: "",
        grok_key_value: "",

        upbit_secret_key: "",
        upbit_access_key: "",

        bingx_secret_key: "",
        bingx_access_key: ""
    });

     // setForm 추가
    useEffect(() => {      
        const data = user_information;
        setForm(prev => ({
            ...prev,
            username: data.Username || "",
            usemodel: data.usemodel || "없음",
            
            // phone: data.phone || "",
            email: data.email || "",
            // post: data.post || "",
            country: data.country || "",
            interval: data.interval || 14400,

            trading_fee: data.trading_fee || "",
            exchange: data.exchange || "없음",
            
            play: data.play || false,
            tier: data.tier || "Master",
            tier_time: data.tier_time || 365,

            ticker: data.ticker || prev.ticker,
            
            user_prompt: data.user_prompt || "",

            gpt_key: data.gpt_key || false,
            grok_key: data.grok_key || false,

            upbit_key: data.upbit_key || false,
            bingx_key: data.bingx_access_key && data.bingx_secret_key ? true : false,    
            
            gpt_key_value: data.gpt_secret_key || "",
            grok_key_value: data.grok_secret_key || "",

            upbit_access_key: data.upbit_access_key || "",
            upbit_secret_key: data.upbit_secret_key || "",

            bingx_access_key: data.bingx_access_key || "",
            bingx_secret_key: data.bingx_secret_key || "",            
        }));
    }, [user_information])
    
    // 기본 탭을 'personal'(개인 설정)로 지정
    const [activeTab, setActiveTab] = useState('personal'); 

    // form 업데이트 헬퍼 (CountrySelect용)
    const updateForm = (key, value) => {
        setForm(prev => ({ ...prev, [key]: value }));
    };

    const renderContent = () => {
        switch (activeTab) {
            case 'personal':
                return (
                    <>
                        <h2 className="content-title">개인 설정</h2>
                        
                        {/* 국가 선택 */}
                        <div className="info-box" style={{marginBottom:'15px'}}>
                            <span className="info-label">국가</span>
                            <div style={{ width: '250px' }}>
                                <CountrySelect form={form} update={updateForm} hideLabel={true} />
                            </div>
                        </div>

                        {/* 등급 */}
                        <div className="info-box" style={{marginBottom:'15px'}}>
                            <span className="info-label">등급</span>
                            <span className="info-value" style={{ fontWeight:'bold', color: '#4a76e8' }}>
                                {form.tier}
                            </span>
                        </div>

                        {/* 등급 유지 기간 */}
                        <div className="info-box" style={{marginBottom:'15px'}}>
                            <span className="info-label">등급 유지 기간</span>
                            <span className="info-value">{form.tier_time} 일</span>
                        </div>

                        {/* 비밀번호 (보안 설정에서 이동) */}
                        <div className="info-box">
                            <span className="info-label">비밀번호</span>
                            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                <span className="info-value">********</span>
                                <button style={{background:'#2962ff', color:'white', border:'none', padding:'6px 12px', borderRadius:'4px', cursor:'pointer', fontSize:'0.85rem'}}>변경</button>
                            </div>
                        </div>
                    </>
                );

            case 'wallet':
                return (
                    <>
                        <Userinfo form={form} setForm={setForm} activeTab="wallet"/>
                    </>
                );
            
            case 'api':
                return (
                    <>
                        <Userinfo form={form} setForm={setForm} activeTab="api"/>
                    </>
                );
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                
                {/* 좌측 사이드바 */}
                <div className="modal-sidebar">
                    <div 
                        className={`sidebar-item ${activeTab === 'personal' ? 'active' : ''}`}
                        onClick={() => setActiveTab('personal')}
                    >
                        <i className="fa-solid fa-user"></i> 개인 설정
                    </div>
                    
                    <div 
                        className={`sidebar-item ${activeTab === 'wallet' ? 'active' : ''}`}
                        onClick={() => setActiveTab('wallet')}
                    >
                        <i className="fa-solid fa-wallet"></i> 현물 거래 설정
                    </div>
                    <div 
                        className={`sidebar-item ${activeTab === 'api' ? 'active' : ''}`}
                        onClick={() => setActiveTab('api')}
                    >
                        <i className="fa-solid fa-key"></i> API 설정
                    </div>
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