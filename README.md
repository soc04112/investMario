# InvestMario (투자 마리오)

**투자 마리오**는 AI(LLM) 기반의 가상화폐 자동매매 및 분석 플랫폼입니다.  
거래소 API를 통해 멀티 거래소 매매를 지원하며, AI를 통한 자동화 된 가상화폐 자동 매매를 지원합니다.
또한 RAG(검색 증강 생성) 기술을 통해 최신 뉴스와 시장 데이터를 분석하여 최적의 매매 포지션을 제안합니다.

## 주요 기능 (Key Features)

* **멀티 거래소 지원:** API를 통한 멀티 거래소 지원 및 가상화폐 자동 매매 기능 지원 
    * **현물(Spot):** Upbit API 연동 및 LLM에 프롬프트를 입력하여 입력된 값에 따라 매매 신호 생성
    * **선물(Futures):** BingX API 연동을 활용한 시장 분석 및 매매 신호 생성
* **RAG 기반 시장 분석:** Function Calling을 활용하여 최신 암호화폐 뉴스 및 기술적 용어 검색 후 AI 판단 근거로 활용
* **실시간 대시보드:** TradingView 차트 연동, 자산 현황, 매매 이력 실시간 모니터링
* **사용자 맞춤 설정:** 투자 성향(공격형/중립형/안전형) 및 레버리지에 따른 사용자 인터렉트

## 기술 스택 (Tech Stack)

### Backend
* **Framework:** Python FastAPI
* **Database:** PostgreSQL, SQLAlchemy
* **AI & Data:** LangChain(implied), FAISS (Vector DB), OpenAI/Google API
* **Authentication:** JWT, Google OAuth

### Frontend
* **Framework:** React (Vite)
* **Styling:** CSS Modules
* **Chart:** TradingView Widget

## 시작하기 (Getting Started)

### 사전 요구 사항
* Python 3.10+
* Node.js 18+
* PostgreSQL

### 설치 및 실행

본 프로젝트를 실행하기 위해 다음과 같은 환경 세팅이 필요합니다.

**1. Backend**
```bash
# requirements 설치
cd backend
pip install -r requirements.txt

#.env 파일 설정 (API Key 등)
FERNET_KEY=FERNET 키 값
GOOGLE_CLOUDE_KEY='구글 클라우드 키 값'
GOOGLE_CLOUDE_IP="구글 클라우드 IP 값"
GOOGLE_OAUTH_CLIENT_ID=구글 OAUTH ID
GOOGLE_OAUTH_CLIENT_SECRET=구글 OAUTH 비밀전호
REDIRECT_URI=http://localhost:3500/oauth/callback
NEWS_DB_PATH="crypto_news_db"
TERM_DB_PATH="crypto_term_db"
OPENAI_API_KEY="OPEN API 키 값"
VLLM_URL="VLLM URL 값"
NEWS_DB_PATH="crypto_news_db"
TERM_DB_PATH="crypto_term_db"
```

**2. Frontend**

```bash
# package 설치
cd frontend
npm install
npm run dev
```

**실행하기**
```bash
#backend
backend\myenv313\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8300 --reload

#frontend
cd frontend
npx vite
```


