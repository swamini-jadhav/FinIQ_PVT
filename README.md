<div align="center">

# FinIQ

**Intelligent Stock Market Analysis Platform**

*LSTM Price Forecasting • Financial Sentiment Analysis • Conversational Assistant*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.x-61dafb?logo=react)](https://reactjs.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-339933?logo=node.js)](https://nodejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)](https://www.mongodb.com/cloud/atlas)
[![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](https://fin-iq-pvt.vercel.app)
[![Deployed on Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://finiq-pvt-1.onrender.com)

</div>

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| 🌐 **Frontend** | [fin-iq-pvt.vercel.app](https://fin-iq-pvt.vercel.app) |
| ⚙️ **Backend API** | [finiq-pvt-1.onrender.com](https://finiq-pvt-1.onrender.com) |
| 🤖 **ML Service** | [finiq-pvt.onrender.com](https://finiq-pvt.onrender.com) |

> ⚠️ **Free tier notes:** Render services spin down after 15 minutes of inactivity — the first
> request may take ~30 seconds to wake up, and can fail outright during the wake window.
> Predictions are cached per ticker for 3 hours; the first request for a given stock trains a
> model while subsequent ones return instantly. The cache is in-memory and clears on restart.

---

## 🚀 Overview

FinIQ combines LSTM time-series forecasting with financial-domain sentiment analysis to turn
raw market data into readable signals. It runs as three services: a React frontend, a
Node/Express API, and a Flask ML microservice, with MongoDB Atlas for persistence.

---

## ✨ Key Features

### 🔐 Secure Authentication
- JWT-based authentication with Passport.js
- Protected routes and per-user sessions
- Bcrypt password hashing

### 📊 LSTM Price Prediction
- Single-layer LSTM (32 hidden units) with a 60-day lookback window
- 8 input features: OHLCV plus SMA-10, EMA-20, RSI-14
- Trained on 2 years of daily data, 15 epochs, per ticker on demand
- Results cached for 3 hours to keep response times usable on free-tier hardware
- **Auto-resolves Indian tickers** — type `TCS` and it finds `TCS.NS`

### 📰 FinBERT Sentiment Analysis
- **Google News RSS** as the primary source, with per-market locale routing so a London
  ticker gets UK coverage and an NSE ticker gets Indian coverage
- Query construction pairs the company name with finance terms, then filters out quote
  pages, price widgets, and other non-editorial results
- **Marketaux** as an automatic fallback when Google News returns thin results, using
  entity-relevance scores to reject index roundups that merely mention the stock
- **FinBERT** (`ProsusAI/finbert`) served through the Hugging Face Inference API — the model
  runs remotely, so no 440 MB download and no local RAM cost
- Positive / Neutral / Negative with confidence scores, mapped to a signed polarity

### 🤖 Investment Assistant
- Rule-based responses across 11 categories for common platform questions
  (how predictions work, supported stocks, accuracy, risk disclaimers, indicators)
- Word-boundary keyword matching with longest-match resolution
- Falls back to an LLM via the Hugging Face router for open-ended questions
- Aware of the ticker currently being viewed

### 📈 Analytics Dashboard
- Chart.js price trends and prediction overlays
- Sentiment distribution across recent articles
- SMA, EMA, and RSI indicators

### 💡 Recommendations
- Buy / Hold / Sell signals from a weighted score
- Combines predicted price movement, model R², and news sentiment
- Every recommendation carries an explicit not-financial-advice disclaimer

---

## 🛠️ Tech Stack

<table>
<tr>
<td valign="top" width="33%">

### Frontend
- ⚛️ **React 18** — component UI
- 🎨 **TailwindCSS** — styling
- 📊 **Chart.js** — visualisation
- 🔀 **React Router v6** — routing
- 🌐 **Axios** — HTTP client

</td>
<td valign="top" width="33%">

### Backend
- 🟢 **Node.js 20** — runtime
- 🚂 **Express.js** — web framework
- 🍃 **MongoDB Atlas** — database
- 📦 **Mongoose** — ODM
- 🔑 **JWT** — auth tokens
- 🛂 **Passport.js** — auth middleware

</td>
<td valign="top" width="33%">

### ML Service
- 🐍 **Flask 3** + **gunicorn**
- 🔥 **PyTorch** — LSTM training
- 🤗 **FinBERT via HF Inference API**
- 📈 **yfinance** — global market data
- 📡 **Google News RSS** + **Marketaux**
- 🔢 **scikit-learn** — scaling, metrics

</td>
</tr>
</table>

### Infrastructure
- 🐳 **Docker** — all three services containerised
- ▲ **Vercel** — frontend hosting
- 🎯 **Render** — backend and ML service hosting
- 🍃 **MongoDB Atlas** — managed database

---

## 📁 Project Structure

```
FinIQ/
│
├── backend/                    # Node.js Express API
│   ├── config/                 # Database & Passport config
│   ├── middleware/             # Auth middleware
│   ├── models/                 # Mongoose schemas
│   ├── routes/                 # auth, ml, chatbot routes
│   ├── server.js               # Express entry point
│   ├── Dockerfile
│   └── package.json
│
├── frontend/                   # React application
│   ├── public/
│   ├── src/
│   │   ├── components/         # Chatbot, charts, shared UI
│   │   ├── context/            # Auth context
│   │   ├── pages/              # Dashboard, Login, Register
│   │   ├── utils/api.js        # Axios instance + endpoint wrappers
│   │   └── App.js
│   ├── Dockerfile              # Multi-stage nginx build
│   ├── nginx.conf
│   └── package.json
│
├── ml-service/                 # Flask ML microservice
│   ├── app.py                  # Flask routes
│   ├── chatbot.py              # Rule-based assistant + LLM fallback
│   ├── lstm_model.py           # LSTM, ticker resolution, prediction cache
│   ├── sentiment_analysis.py   # News retrieval + FinBERT classification
│   ├── Dockerfile              # Slim image, gunicorn entrypoint
│   └── requirements.txt        # Pinned dependencies
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites

- **Node.js** v20+
- **Python** 3.10+
- **MongoDB Atlas** account — [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- **Hugging Face** token — [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- **Marketaux** key (optional, fallback only) — [marketaux.com](https://www.marketaux.com/)

---

### Option A — Docker

```bash
git clone https://github.com/swamini-jadhav/FinIQ_PVT.git
cd FinIQ_PVT
# create the .env files described below, then:
docker-compose up --build
```

Open **http://localhost:3000**. First build takes 3–5 minutes, mostly PyTorch.

---

### Option B — Run each service manually

Three terminals, one per service.

#### 1️⃣ ML service

```bash
cd ml-service
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

Create `ml-service/.env`:
```env
FLASK_PORT=5001
FLASK_ENV=development
HF_TOKEN=hf_your_huggingface_token
MARKETAUX_KEY=your_marketaux_key
```

```bash
python app.py                     # http://localhost:5001
```

#### 2️⃣ Backend

```bash
cd backend
npm install
```

Create `backend/.env`:
```env
PORT=5000
MONGODB_URI=your_mongodb_atlas_connection_string
JWT_SECRET=your_jwt_secret
SESSION_SECRET=your_session_secret
NODE_ENV=development
FRONTEND_URL=http://localhost:3000
ML_SERVICE_URL=http://localhost:5001
```

```bash
npm run dev                       # http://localhost:5000
```

#### 3️⃣ Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ML_API_URL=http://localhost:5001
```

```bash
npm start                         # http://localhost:3000
```

> Each `.env` file must contain one variable per line, and the filename must start with a dot.

---

## 🔑 Required Keys

| Key | Where to get it | Used for |
|-----|----------------|----------|
| `MONGODB_URI` | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free M0 tier) | User accounts and favourites |
| `HF_TOKEN` | [huggingface.co](https://huggingface.co/settings/tokens) (read scope) | FinBERT sentiment + chatbot LLM fallback |
| `MARKETAUX_KEY` | [marketaux.com](https://www.marketaux.com/) (free tier) | Fallback news source — optional |

Google News RSS is the primary news source and requires no key or account.

---

## 📡 API Endpoints

### ML Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check, reports key configuration |
| `POST` | `/predict` | LSTM price prediction (cached 3h per ticker) |
| `POST` | `/news-sentiment` | FinBERT sentiment over recent company news |
| `POST` | `/recommendation` | Prediction + sentiment + weighted signal |
| `POST` | `/chatbot` | Assistant response |

### Backend

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create account |
| `POST` | `/api/auth/login` | Log in, returns JWT |
| `GET` | `/api/auth/user` | Current user |
| `PUT` | `/api/auth/favorites` | Update watchlist |
| `POST` | `/api/ml/predict` | Prediction proxy |
| `POST` | `/api/ml/news-sentiment` | Sentiment proxy |
| `POST` | `/api/ml/recommendation` | Recommendation proxy |
| `GET` | `/api/ml/health` | ML service health proxy |
| `POST` | `/api/chatbot/query` | Chatbot proxy |
| `POST` | `/api/chatbot/feedback` | Response feedback |

---

## 🌍 Market Coverage

Price data comes from Yahoo Finance and news is routed to a market-appropriate locale, so
the platform works across major global exchanges:

| Market | Suffix | Example | News locale |
|--------|--------|---------|-------------|
| United States | *(none)* | `AAPL`, `TSLA` | US |
| India (NSE) | `.NS` | `TCS.NS`, `RELIANCE.NS` | IN |
| India (BSE) | `.BO` | `TCS.BO` | IN |
| London | `.L` | `BARC.L`, `SHEL.L` | GB |
| Tokyo | `.T` | `7203.T` | JP |
| Frankfurt | `.DE` | `SAP.DE` | DE |
| Hong Kong | `.HK` | `0700.HK` | HK |
| Others | `.PA` `.AX` `.TO` `.SW` `.SS` | — | matched |

**Ticker auto-resolution currently covers Indian and US symbols only.** Typing `TCS` resolves
to `TCS.NS`, but a London or Tokyo listing needs the suffix typed explicitly (`BARC.L`, not
`BARC`).

---

## ☁️ Deployment

Three services, deployed in this order. The order matters because each needs the previous
one's URL.

### 1. ML service — Render

- New Web Service → Runtime **Docker** → Root Directory `ml-service`
- Health Check Path: `/health`
- Environment: `HF_TOKEN`, `MARKETAUX_KEY`
- **Do not set `PORT` or `FLASK_PORT`** — Render injects `PORT` and the app reads it

### 2. Backend — Render

- New Web Service → Runtime **Docker** → Root Directory `backend`
- Health Check Path: `/health`
- Environment: `MONGODB_URI`, `JWT_SECRET`, `SESSION_SECRET`, `NODE_ENV=production`,
  `ML_SERVICE_URL` (the ML service URL), `FRONTEND_URL` (placeholder for now)
- MongoDB Atlas → Network Access must allow `0.0.0.0/0`; free-tier outbound IPs are not
  static, and the server exits on a failed database connection

### 3. Frontend — Vercel

- Import project → **Root Directory `frontend`**
- Environment: `REACT_APP_API_URL`, `REACT_APP_ML_API_URL`
- Create React App inlines `REACT_APP_*` at build time, so **any change requires a redeploy**

### 4. Close the loop

Set `FRONTEND_URL` on the backend to the Vercel URL. This is the CORS origin — if it doesn't
match exactly (scheme included, no trailing slash), every browser request fails.

### URL reference

| Variable | Set on | Value |
|----------|--------|-------|
| `ML_SERVICE_URL` | Render → backend | ML service URL |
| `FRONTEND_URL` | Render → backend | Vercel URL |
| `REACT_APP_API_URL` | Vercel | Backend URL |
| `REACT_APP_ML_API_URL` | Vercel | ML service URL |

No URLs are hardcoded in source — all three services read them from the environment.

---

## ⚙️ Free-Tier Engineering Notes

Running this on Render's free tier (512 MB RAM, ~0.1 shared CPU) drove several decisions:

- **FinBERT runs remotely.** Loading a 440 MB transformer locally exceeded the memory limit
  and killed the worker, so sentiment inference moved to the Hugging Face Inference API.
- **`torch.set_num_threads(1)`.** PyTorch otherwise spawns one thread per detected host core;
  on a fractional CPU allocation those threads contend and training slows dramatically. This
  single change cut prediction time by several minutes.
- **Reduced model capacity.** Single layer, 32 hidden units — chosen to fit the compute budget
  and because the larger configuration showed no accuracy benefit here.
- **Prediction caching.** Retraining per request could not fit inside the API gateway timeout.
  A 3-hour in-memory cache keyed by ticker makes repeat requests immediate.
- **Pinned dependencies.** An unpinned `yfinance` upgrade changed its return format to
  MultiIndex columns and broke predictions silently. All versions are now pinned.

---

## ⚠️ Known Limitations

- Models train on demand rather than from saved weights; a production version would train
  offline and serve inference only.
- The scaler is currently fitted on the full dataset before the train/test split, which leaks
  test-set range into normalisation and inflates the reported R². Fitting on the training
  portion only is the correct approach.
- Google News RSS is an unofficial endpoint with no stability guarantee. Marketaux is
  configured as a fallback, but a change to the RSS format would need a code update.
- Google News RSS provides headlines without article summaries, so FinBERT classifies titles
  rather than full text.
- Company-specific news is sparse for some listings between quarterly results, particularly
  outside the US. Sentiment for those tickers may reflect sector or index coverage.
- Predictions are a single-step next-close estimate. This is a learning project, not
  investment advice.

---

## 🤝 Contributors

<table>
<tr>
    <td align="center">
        <a href="https://github.com/swamini-jadhav">
            <img src="https://github.com/swamini-jadhav.png" width="100px;" alt="Swamini Jadhav"/>
            <br /><sub><b>Swamini Jadhav</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/muskaankarwa">
            <img src="https://github.com/muskaankarwa.png" width="100px;" alt="Muskaan Karwa"/>
            <br /><sub><b>Muskaan Karwa</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/sahilapage">
            <img src="https://github.com/sahilapage.png" width="100px;" alt="Sahil Apage"/>
            <br /><sub><b>Sahil Apage</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/aaradhanac07">
            <img src="https://github.com/aaradhanac07.png" width="100px;" alt="Aaradhana Chaudhary"/>
            <br /><sub><b>Aaradhana Chaudhary</b></sub>
        </a>
    </td>
</tr>
</table>

---

## 📝 License

MIT — see [LICENSE](LICENSE).

---

## 🌟 Roadmap

- [ ] Train models offline and serve saved weights
- [ ] Persist the prediction cache in MongoDB so it survives restarts
- [ ] Extend ticker auto-resolution to European and Asian exchanges
- [ ] Multi-stock portfolio tracking
- [ ] MACD and Bollinger Bands
- [ ] Price alerts
- [ ] WebSocket price streaming

---

<div align="center">
Made by the FinIQ Team
</div>