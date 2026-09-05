# 🛡️ Razorpay Risk Sentinel

**Real-Time Fraud-Spike Containment & Rupee-Denominated Cost Tracking**

Razorpay Risk Sentinel is a full-stack, dual-brain fraud detection system designed to protect e-commerce merchants from high-velocity card-testing bots and checkout fraud. It intercepts transactions in real-time, evaluates them using a lightweight Machine Learning model (LightGBM), and utilizes an AI Copilot to provide actionable reasoning for transaction holds.

### 🚀 Live Demo
- **Interactive Split-Screen Demo:** [Live on Vercel](https://razorpay-risk-sentinel-ju1o.vercel.app/demo.html)
- **Backend API:** [Hosted on Render](https://razorpay-backend-g943.onrender.com)


## 💻 Local Development Setup

To run this project locally, you will need two terminal windows: one for the backend server and one for the frontend client.

### 1. Start the Backend (FastAPI)
Open your first terminal, navigate to the backend folder, and start the Python server:

```bash
cd backend
# Install dependencies
pip install -r requirements.txt
# Run the training engine to generate detector.pkl (if missing)
python engine.py
# Start the uvicorn server
uvicorn server:app --reload --port 8000

2. Start the Frontend (React + Vite)
Open a new second terminal at the root of the project:

Bash
# Install dependencies
npm install
# Start the development server
npm run dev

---

## ⚡ Key Features

* **Dual-Brain Architecture:** Uses LightGBM for sub-millisecond initial risk scoring, backed by an LLM-based Copilot to analyze edge cases and provide natural language reasoning.
* **Real-Time WebSocket Streaming:** The React dashboard connects to a FastAPI WebSocket endpoint to visualize transaction velocity and risk scores live.
* **Interactive Storefront Simulation:** Features a mock e-commerce checkout to manually trigger and visualize bot attacks (20x rapid requests) or genuine user edge cases (fast double-clicks).
* **Automated Mitigation Audit Trail:** Logs transaction IDs, 3-minute rolling velocity, risk scores, and the AI's final mitigation decision.

---

## 🛠️ Tech Stack

**Frontend:**
* React.js (Vite)
* Recharts (Real-time data visualization)
* Vercel (Production hosting)

**Backend:**
* Python / FastAPI
* LightGBM & Pandas (Data Processing & ML Engine)
* WebSockets (Bi-directional streaming)
* Render (Production hosting)

---

## 📂 Project Structure

```text
razorpay-risk-sentinel/
├── backend/                # FastAPI & ML Engine
│   ├── data/               # CSV datasets for simulation
│   ├── engine.py           # LightGBM training & feature engineering script
│   ├── server.py           # FastAPI WebSocket & REST endpoints
│   ├── requirements.txt    # Python dependencies
│   └── detector.pkl        # Serialized ML model
├── public/                 # Static Assets for Frontend
│   ├── demo.html           # Split-screen iframe wrapper (Main Demo)
│   ├── store.html          # Mock e-commerce storefront layout
│   └── vite.svg
├── src/                    # React Frontend Source
│   ├── App.jsx             # Real-time Dashboard with WebSockets
│   ├── main.jsx            # React DOM entry point
│   └── index.css           # Global styles
├── package.json            # Node dependencies
├── vite.config.js          # Vite build configuration
├── vercel.json             # Vercel deployment routing config
└── README.md               # Project documentation
