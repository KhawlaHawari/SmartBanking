# 🏦 SmartBanking AI Platform

> An end-to-end AI-powered banking analytics platform for customer segmentation, risk scoring, churn prediction, and next-best-action recommendations — built with FastAPI, React, and Google Gemini.


---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [ML Models](#ml-models)
- [Dataset](#dataset)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Chatbot](#chatbot)
- [Project Notes](#project-notes)

---

## 🔍 Overview

SmartBanking is a full-stack intelligent banking platform that combines machine learning, real-time predictions, and an AI assistant to help analysts understand customer behavior at scale.

**Key features:**
- 🎯 **Customer Segmentation** — Classify customers into 6 behavioral segments
- ⚠️ **Risk Detection** — Identify high-risk customers before they default
- 📉 **Churn Prediction** — Predict which customers are likely to leave
- 💡 **Action Recommendation** — Suggest the best next action for each customer
- 📊 **EDA Dashboard** — Visual analytics on the full customer dataset
- 📁 **Batch Upload** — Score entire Excel files at once
- 🤖 **AI Chatbot** — Gemini-powered assistant with full dataset context

---

## 🏗️ Architecture

```
SmartBanking/
├── smart-banking/
│   ├── backend/                  ← FastAPI Python backend
│   │   ├── app/
│   │   │   ├── models/           ← ML training & prediction logic
│   │   │   ├── routes/           ← API route handlers
│   │   │   ├── schemas/          ← Pydantic request/response models
│   │   │   ├── utils/            ← Config, logging, chat engine
│   │   │   ├── database.py       ← SQLite async setup
│   │   │   ├── load_data.py      ← Model & dataset loading cache
│   │   │   └── main.py           ← FastAPI app entry point
│   │   ├── saved_models/         ← Trained .pkl model artifacts
│   │   ├── data/                 ← Dataset (Excel)
│   │   ├── requirements.txt
│   │   └── .env
│   └── frontend/                 ← React + Vite frontend
│       ├── src/
│       │   └── App.jsx           ← Main UI (dashboard, predict, chat)
│       ├── .env
│       └── package.json
```

---

## 🤖 ML Models

Four machine learning models are trained and deployed in production:

| Model | Algorithm | Performance |
|-------|-----------|-------------|
| **Customer Segmentation** | RandomForestClassifier (n=400, balanced) | Accuracy: 84.4% · F1-macro: 0.82 |
| **Risk Detection** | GradientBoosting + CalibratedClassifierCV | AUC-ROC: 1.0* · Recall: 100% |
| **Churn Prediction** | RandomForestClassifier + CalibratedClassifierCV | AUC-ROC: 1.0* · F1: 0.994 |
| **Action Recommendation** | RandomForestClassifier (n=400, balanced) | Accuracy: 91.7% · Top-3: 100% |

> ⚠️ **Note on perfect scores:** Risk and churn models achieve near-perfect scores because the dataset is synthetically generated with clear decision boundaries. In a real-world production environment with noisy, overlapping data, scores would realistically be lower. The segmentation (F1=0.82) and action recommendation (Accuracy=0.917) models reflect more realistic performance levels.

**Supported customer segments:** Active, Premium, Standard, VIP, At-Risk, Strategic Premium

**Supported recommended actions:** Financial Advisory, Debt Restructuring, Digital Engagement, Credit Review, Credit Freeze, Proactive Outreach

---

## 📊 Dataset

The platform uses a **synthetically generated** dataset (`bank_customer_dataset.xlsx`) with **4,999 customer records** and the following features:

| Category | Features |
|----------|----------|
| Demographics | `age`, `gender`, `region`, `employment_status` |
| Financial | `monthly_income`, `credit_score`, `credit_utilization` |
| Behavioral | `num_products`, `tenure_months`, `days_since_last_activity` |
| Risk Indicators | `num_defaults`, `num_late_payments`, `complaint_count` |

> The dataset was designed to simulate realistic banking customer distributions, enabling a full demonstration of the ML pipeline. It is not derived from real customer data.

---

## 🔌 API Endpoints

### Health & Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Returns API and model readiness status |
| `GET` | `/api/stats` | Returns aggregated dashboard statistics |

### Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Single customer prediction (all 4 models) |
| `POST` | `/api/predict/batch` | Batch prediction for multiple customers |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics` | Model training metrics and performance |
| `GET` | `/api/eda` | EDA statistics (distributions, correlations) |
| `POST` | `/api/upload` | Upload Excel file for batch scoring |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message to AI assistant |
| `GET` | `/api/chat/models` | List available Gemini models |
| `DELETE` | `/api/chat/{session_id}` | Clear chat session history |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/request-otp` | Request OTP code via email |
| `POST` | `/auth/verify-otp` | Verify OTP and get access token |
| `POST` | `/auth/login` | Login with credentials |

Full interactive API documentation available at: `http://localhost:8023/docs`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 (required — Python 3.14 has dependency compatibility issues)
- Node.js 18+
- Git

### Backend Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd smart-banking/backend

# 2. Create and activate Python 3.11 virtual environment
py -3.11 -m venv .venv311
.venv311\Scripts\activate        # Windows
# source .venv311/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in your values (see Environment Variables section)

# 5. Regenerate ML model artifacts
python -m app.models.train

# 6. Start the backend server
python -m uvicorn app.main:app --port 8023
```

Backend will be available at: `http://localhost:8023`

### Frontend Setup

```bash
# In a new terminal
cd smart-banking/frontend

# 1. Install dependencies
npm install

# 2. Configure API URL
# Edit .env and set:
# VITE_API_URL=http://localhost:8023

# 3. Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## ⚙️ Environment Variables

Create a `.env` file in `smart-banking/backend/`:
```env
# AI Chatbot
GROQ_API_KEY=your_groq_api_key_here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Database
DATABASE_URL=sqlite:///./smartbank.db

# Authentication
SECRET_KEY=your_long_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (OTP)
EMAIL_DEMO_MODE=True          # Set False to send real emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your_app_password

# Server
API_HOST=0.0.0.0
API_PORT=8023
MAX_UPLOAD_SIZE_MB=10
```

> Get a free Groq API key at: https://console.groq.com

---

## 🤖 Chatbot

The SmartBanking AI assistant is powered by **Groq (LLaMA 3)** via the `groq` SDK.

**How it works:**
1. On every request, the system prompt is dynamically built with full dataset context: row count, column names, churn rate, segment distribution, risk distribution, and model training metrics
2. Conversation history is maintained per session (last 10 messages) using in-memory storage
3. The assistant can answer questions about customer segments, risk levels, churn rates, model performance, and platform usage

**Fallback behavior:** If the Groq API is unavailable (quota exceeded or missing key), the chatbot falls back to a local keyword-based response system covering the most common analytics questions.

---

## 📝 Project Notes

- **Python version:** Always use Python 3.11. Python 3.14 breaks several ML dependencies (numpy, scikit-learn, lightgbm)
- **Model retraining:** Run `python -m app.models.train` after a fresh install to generate `.pkl` artifacts compatible with your installed scikit-learn version
- **Startup sequence:** FastAPI lifespan loads all model artifacts and dataset into memory at startup for fast inference
- **Configuration:** All settings are managed through `app/utils/config.py` using `pydantic-settings` with `.env` file support
- **Database:** SQLite with async support via `aiosqlite` — no external database required
- **Authentication:** OTP-based email authentication with JWT tokens. Set `EMAIL_DEMO_MODE=True` to print OTP codes to terminal during development

---

## 👥 Authors

SmartBanking AI Platform — Khawla El Haouri

---

*Built with FastAPI · React · scikit-learn · LightGBM · Groq*