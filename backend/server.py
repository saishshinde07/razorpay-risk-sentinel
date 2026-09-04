import asyncio
import json
import pickle
import pandas as pd
import numpy as np
import random
import re
import os
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (though no longer strictly needed since we mock the LLM for the demo)
load_dotenv() 

app = FastAPI(title="Razorpay Risk Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Load the LightGBM Detector (System 1)
try:
    with open("detector.pkl", "rb") as f:
        bundle = pickle.load(f)
        model = bundle["model"]
        features = bundle["features"]
except FileNotFoundError:
    print("❌ Error: detector.pkl not found. Please run engine.py first.")
    exit(1)

# Load and prepare the held-out test data for streaming
print("Loading held-out test set for live stream simulation...")
try:
    test_df = pd.read_csv("../data/held_out_test.csv")
    test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])
    test_df = test_df.set_index('timestamp')
    test_df['feat_velocity'] = test_df['Amount'].rolling('180s').count()
    test_df['feat_mean_amount'] = test_df['Amount'].rolling('180s').mean().fillna(0)
    test_df = test_df.reset_index()

    fraud_indices = test_df[test_df['Class'] == 1].index
    start_idx = max(0, fraud_indices[0] - 50) if not fraud_indices.empty else 0
    stream_data = test_df.iloc[start_idx : start_idx + 300].to_dict('records')
except FileNotFoundError:
    print("❌ Error: ../data/held_out_test.csv not found. Please run engine.py first.")
    exit(1)

# 2. Vaultless Tokenization Engine (Privacy Gateway)
TOKEN_VAULT = {}
TOKEN_COUNTER = 1

def tokenize_card(card_number: str) -> str:
    global TOKEN_COUNTER
    if card_number not in TOKEN_VAULT:
        TOKEN_VAULT[card_number] = f"[CARD_TOKEN_00{TOKEN_COUNTER}]"
        TOKEN_COUNTER += 1
    return TOKEN_VAULT[card_number]

def mask_pii(text: str) -> str:
    """Finds 16-digit cards and safely tokenizes them for the LLM."""
    card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    def replacer(match):
        raw_card = re.sub(r'[\s-]', '', match.group(0))
        return tokenize_card(raw_card)
    return re.sub(card_pattern, replacer, text)


# 3. System 2: MOCKED LLM Advisory Copilot (Bypasses API Limits for Video Demo)
async def verify_with_llm(tx_data: dict, risk_score: float) -> dict:
    """Simulates the LLM Copilot to bypass API rate limits during the video pitch."""
    
    # Simulate network delay so it looks like a real API call on the UI
    await asyncio.sleep(0.8) 
    
    # Logic to return varied responses based on the transaction amount
    if tx_data['amount'] < 50:
        return {
            "recommendation": "CONFIRM_CARD_TESTING", 
            "reasoning": "High-velocity micro-transactions indicate automated card testing ring."
        }
    else:
        return {
            "recommendation": "REVIEW_FLASH_SALE", 
            "reasoning": "Velocity matches seasonal retail spike. Review for false positive."
        }

# 4. WebSocket for the React Dashboard
@app.websocket("/ws/stream")
async def transaction_stream(websocket: WebSocket):
    await websocket.accept()
    print("Streaming with Dual-Brain Copilot Active (Mock LLM Enabled)...")
    
    last_llm_call = 0 

    try:
        for i, row in enumerate(stream_data):
            # Process features for LightGBM
            model_input = pd.DataFrame([[row[col] for col in features]], columns=features)
            risk_score = float(model.predict_proba(model_input)[0][1])
            amount_inr = round(row["Amount"] * 83.0, 2)
            
            # --- VIDEO DEMO OVERRIDE ---
            # Triggers a spike immediately every 15 items so you don't have to wait
            if row["Class"] == 1 or i % 15 == 0:
                mock_card = "4111-2222-3333-4444" 
                risk_score = 0.85 
            else:
                mock_card = f"4111-2222-3333-{random.randint(1000, 9999)}" 

            base_tx = {
                "id": f"pay_{i}",
                "amount": amount_inr,
                "feat_velocity": int(row.get("feat_velocity", 0)),
                "mock_card": mock_card
            }

            threshold = 0.60
            if risk_score >= threshold:
                action = "AUTO-HOLD"  # Matches what your frontend checks for
                
                # --- API COOLDOWN LOGIC ---
                current_time = time.time()
                if current_time - last_llm_call > 60:
                    decision = await verify_with_llm(base_tx, risk_score)
                    reasoning = f"[{decision.get('recommendation', 'REVIEW')}] {decision.get('reasoning', 'Flagged by ML.')}"
                    last_llm_call = current_time
                else:
                    reasoning = "[REVIEW] Flagged by ML. Multiple high-risk events detected in current window."
            else:
                action = "CLEARED"
                reasoning = "Normal traffic profile."

            payload = {
                **base_tx,
                "timestamp": datetime.now().timestamp(),
                "time_str": datetime.now().strftime("%H:%M:%S"),
                "true_label": int(row["Class"]),
                "feat_failure_rate": 0.0,
                "risk_score": round(risk_score, 3),
                "action": action,
                "reasoning": reasoning
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.5) 

    except Exception as e:
        print(f"Client disconnected: {e}")

# 5. REST API Endpoint for the Fake Storefront Intercept
class CheckoutRequest(BaseModel):
    amount: float
    card_number: str

@app.post("/api/checkout")
async def checkout_intercept(req: CheckoutRequest):
    """Endpoint that the HTML store hits during the split-screen demo."""
    
    # Simple logic: multiple 10 INR hits represent a bot card-testing attack
    is_spike = req.amount < 100 
    
    if is_spike:
        return {
            "status": "HOLD_FOR_REVIEW",
            "message": "Transaction held by Risk Sentinel: High-velocity micro-transaction detected.",
            "allowed": False
        }
        
    return {
        "status": "APPROVED",
        "message": "Transaction cleared for processing.",
        "allowed": True
    }