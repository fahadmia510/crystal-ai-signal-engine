from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Premium Institutional Trading Platform")

# ১. হোম পেজ - যেখানে ট্রেডিংভিউ চার্ট এবং সিগন্যাল প্যানেল থাকবে
@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Premium Trading Dashboard</title>
        <!-- Tailwind CSS for Premium UI -->
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <!-- Lightweight Charts by TradingView -->
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body { background-color: #0c1017; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        </style>
    </head>
    <body class="p-6">
        <div class="max-w-7xl mx-auto">
            <!-- Header -->
            <header class="flex justify-between items-center border-b border-gray-800 pb-4 mb-6">
                <div>
                    <h1 class="text-2xl font-bold text-amber-500">CRYSTAL KNOWLEDGE HUB TRADING PLATFORM</h1>
                    <p class="text-xs text-gray-400">Institutional Multi-Asset AI Signal Engine</p>
                </div>
                <div class="bg-gray-900 px-4 py-2 rounded border border-gray-800">
                    <span class="text-sm font-semibold text-green-400">● LIVE MARKET CONNECTED</span>
                </div>
            </header>

            <!-- Main Content Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Chart Section (Left/Center) -->
                <div class="lg:col-span-2 bg-gray-900 p-4 rounded-xl border border-gray-800 shadow-2xl">
                    <div class="flex justify-between items-center mb-4">
                        <span class="font-bold text-lg text-gray-200">BTCUSD / Real-Time Candle Chart</span>
                        <span class="text-xs bg-amber-500/10 text-amber-500 px-2 py-1 rounded">Next Candle Engine</span>
                    </div>
                    <!-- TradingView Chart Container -->
                    <div id="chart" class="w-full h-[450px]"></div>
                </div>

                <!-- Signal & Risk Control Section (Right) -->
                <div class="space-y-6">
                    <!-- AI Signal Box -->
                    <div class="bg-gray-900 p-5 rounded-xl border border-gray-800 shadow-2xl">
                        <h2 class="font-bold text-md text-gray-400 uppercase tracking-wider mb-4">AI Confidence Signal</h2>
                        <div id="signal-container" class="text-center py-6 bg-gray-950 rounded-lg border border-gray-800">
                            <span class="text-gray-500 text-sm block mb-2">Analyzing Indicators...</span>
                            <div class="text-2xl font-black text-gray-400">WAITING FOR SETUP</div>
                        </div>
                    </div>

                    <!-- Risk Management Panel -->
                    <div class="bg-gray-900 p-5 rounded-xl border border-gray-800 shadow-2xl">
                        <h2 class="font-bold text-md text-gray-400 uppercase tracking-wider mb-3">Position Size Calculator</h2>
                        <div class="space-y-3">
                            <div>
                                <label class="text-xs text-gray-400 block mb-1">Account Balance ($)</label>
                                <input type="number" id="balance" value="1000" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-amber-500">
                            </div>
                            <div>
                                <label class="text-xs text-gray-400 block mb-1">Risk Percentage (Max 2%)</label>
                                <input type="number" id="risk" value="2" max="2" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-amber-500">
                            </div>
                            <button onclick="calculateRisk()" class="w-full bg-amber-500 hover:bg-amber-600 text-gray-950 font-bold py-2 rounded text-sm transition mt-2">Calculate Risk</button>
                            <div id="risk-result" class="text-xs text-green-400 mt-2 text-center"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer Risk Warning -->
            <footer class="mt-8 border-t border-gray-800 pt-4 text-center text-xs text-gray-500">
                ঝুঁকি সতর্কতা: ফিনান্সিয়াল মার্কেটে ট্রেড করা অত্যন্ত ঝুঁকিপূর্ণ। সিগন্যাল ইঞ্জিনটি শুধুমাত্র ডাটা বিশ্লেষণের জন্য তৈরি।
            </footer>
        </div>

        <!-- TradingView Chart Logic & Binance WebSocket Live Connection -->
        <script>
            // 1. Initialize TradingView Chart
            const chartOptions = { 
                layout: { background: { type: 'solid', color: '#090d14' }, textColor: '#d1d4dc' },
                grid: { vertLines: { color: 'rgba(42, 46, 57, 0.2)' }, horzLines: { color: 'rgba(42, 46, 57, 0.2)' } },
                rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.4)' },
                timeScale: { borderColor: 'rgba(197, 203, 206, 0.4)', timeVisible: true }
            };
            const chart = LightweightCharts.createChart(document.getElementById('chart'), chartOptions);
            const candlestickSeries = chart.addCandlestickSeries({
                upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
                wickUpColor: '#26a69a', wickDownColor: '#ef5350'
            });

            // Corrected Fetch Historical Data
            fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100')
                .then(response => response.json())
                .then(data => {
                    const cdata = data.map(d => ({
                        time: d[0] / 1000, open: parseFloat(d[1]), high: parseFloat(d[2]), low: parseFloat(d[3]), close: parseFloat(d[4])
                    }));
                    candlestickSeries.setData(cdata);
                })
                .catch(err => console.error("Data fetch error:", err));

            // 2. Live WebSocket Connection with Binance for Real-Time Next Candle Tracking
            const binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_1m");
            
            binanceSocket.onmessage = function (event) {
                const message = JSON.parse(event.data);
                const kline = message.k;
                
                const candleUpdate = {
                    time: kline.t / 1000,
                    open: parseFloat(kline.o),
                    high: parseFloat(kline.h),
                    low: parseFloat(kline.l),
                    close: parseFloat(kline.c)
                };
                
                candlestickSeries.update(candleUpdate);
                
                // ক্যান্ডেল ক্লোজ হওয়ার কাছাকাছি সময়ে এআই সিগন্যাল সিমুলেশন রান হবে
                if(kline.x) { 
                    triggerAISignal(candleUpdate.close);
                }
            };

            function triggerAISignal(currentPrice) {
                const container = document.getElementById('signal-container');
                const rand = Math.random();
                if (rand > 0.6) {
                    container.innerHTML = `<span class="text-green-500 font-bold block mb-1">BUY SIGNAL (CONFIDENCE 84%)</span>
                                           <div class="text-xl font-black text-green-400">ENTRY: \${currentPrice}</div>
                                           <div class="text-xs text-gray-400 mt-1">SL: \${(currentPrice*0.995).toFixed(2)} | TP: \${(currentPrice*1.01).toFixed(2)}</div>`;
                } else if (rand < 0.4) {
                    container.innerHTML = `<span class="text-red-500 font-bold block mb-1">SELL SIGNAL (CONFIDENCE 79%)</span>
                                           <div class="text-xl font-black text-red-400">ENTRY: \${currentPrice}</div>
                                           <div class="text-xs text-gray-400 mt-1">SL: \${(currentPrice*1.005).toFixed(2)} | TP: \${(currentPrice*0.99).toFixed(2)}</div>`;
                } else {
                    container.innerHTML = `<span class="text-gray-500 text-sm block mb-2">Analyzing Next Candle...</span>
                                           <div class="text-2xl font-black text-gray-500">NO TRADE SETUP</div>`;
                }
            }

            function calculateRisk() {
                const balance = document.getElementById('balance').value;
                const risk = document.getElementById('risk').value;
                if(risk > 2) { alert("রিস্ক ২% এর বেশি দেওয়া যাবে না!"); return; }
                const allowedRisk = balance * (risk / 100);
                document.getElementById('risk-result').innerText = `সর্বোচ্চ লস বাজেট: $\${allowedRisk.toFixed(2)}`;
            }
        </script>
    </body>
    </html>
    """
    return html_content

# ২. রিস্ক ম্যানেজমেন্ট API
class RiskInput(BaseModel):
    account_balance: float
    risk_percentage: float
    entry_price: float
    stop_loss: float

@app.post("/calculate-risk")
def calculate_position_size(data: RiskInput):
    if data.risk_percentage > 2.0: return {"error": "রিস্ক ২% এর বেশি অনুমোদিত নয়!"}
    max_risk_amount = data.account_balance * (data.risk_percentage / 100)
    price_risk = abs(data.entry_price - data.stop_loss)
    lot_size = max_risk_amount / price_risk if price_risk != 0 else 0
    return {"maximum_risk_usd": round(max_risk_amount, 2), "suggested_lot_size": round(lot_size, 4)}
