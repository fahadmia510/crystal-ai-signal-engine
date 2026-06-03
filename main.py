from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd

app = FastAPI(title="Crystal AI Live Signal Engine")

# CORS এনাবল করা হচ্ছে যেন আপনার ওয়েবসাইট এই ব্যাকএন্ড অ্যাক্সেস করতে পারে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_live_indicators():
    try:
        # বাইনান্স থেকে লাইভ ও ঐতিহাসিক ক্যান্ডেলস্টিক ডাটা নেওয়া (১ মিনিটের ক্যান্ডেল)
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
        response = requests.get(url).json()
        
        # ডাটা ফ্রেমে রূপান্তর
        df = pd.DataFrame(response, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'tbb', 'tbq', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        
        # ১. RSI ক্যালকুলেশন (আসল টেকনিক্যাল ইন্ডিকেটর)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # ২. সাধারণ অর্ডার ব্লক/মার্কেট স্ট্রাকচার চেক (সিম্পল এআই লজিক)
        last_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        
        # সিগন্যাল লজিক (আপনার প্রম্পটের নিয়ম অনুযায়ী)
        confidence = 50
        signal = "NO TRADE SETUP"
        
        if current_rsi < 35 and last_close > prev_close:
            signal = "BUY"
            confidence = 82
        elif current_rsi > 65 and last_close < prev_close:
            signal = "SELL"
            confidence = 78
            
        return {
            "signal": signal,
            "confidence": f"{confidence}%",
            "rsi": round(current_rsi, 2),
            "current_price": last_close,
            "sl": round(last_close * 0.995, 2) if signal == "BUY" else round(last_close * 1.005, 2),
            "tp": round(last_close * 1.01, 2) if signal == "BUY" else round(last_close * 0.99, 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/live-signal")
def get_live_signal():
    # রিয়েল টাইমে ইন্ডিকেটর হিসাব করে সিগন্যাল রিটার্ন করবে
    data = fetch_live_indicators()
    return data
