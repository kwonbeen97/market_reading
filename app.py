"""
Flask 웹 서버 - 코스피/나스닥 주도 종목 대시보드
"""
from flask import Flask, jsonify, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "market_data.json"

HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>시장 주도 종목</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f1117; color: #e8eaed; min-height: 100vh; }
  .header { padding: 20px 16px 12px;
            background: linear-gradient(135deg, #1a1d27 0%, #0f1117 100%);
            border-bottom: 1px solid #2a2d3a; }
  .header h1 { font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }
  .header .date { font-size: 12px; color: #888; margin-top: 4px; }
  .refresh-btn { float: right; background: #2563eb; color: #fff;
                 border: none; border-radius: 8px; padding: 6px 14px;
                 font-size: 13px; cursor: pointer; margin-top: -2px; }
  .tabs { display: flex; padding: 12px 16px 0; gap: 8px; }
  .tab { flex: 1; padding: 10px; text-align: center; font-size: 14px;
         font-weight: 600; border-radius: 10px 10px 0 0; cursor: pointer;
         background: #1a1d27; color: #888; border: 1px solid #2a2d3a;
         border-bottom: none; transition: all 0.2s; }
  .tab.active { background: #1e2235; color: #e8eaed; border-color: #3a3d4a; }
  .content { padding: 0 16px 20px; }
  .section { margin-top: 16px; }
  .section-title { font-size: 13px; font-weight: 600; color: #888;
                   text-transform: uppercase; letter-spacing: 0.5px;
                   margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
  .dot-up { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; }
  .dot-down { width: 6px; height: 6px; border-radius: 50%; background: #ef4444; }
  .card { background: #1a1d27; border-radius: 12px; overflow: hidden;
          border: 1px solid #2a2d3a; }
  .stock-row { display: flex; align-items: center; padding: 12px 14px;
               border-bottom: 1px solid #2a2d3a; }
  .stock-row:last-child { border-bottom: none; }
  .rank { font-size: 12px; color: #555; width: 20px; flex-shrink: 0; }
  .name { flex: 1; font-size: 15px; font-weight: 500; }
  .price { font-size: 13px; color: #888; margin-right: 12px; }
  .change { font-size: 15px; font-weight: 700; min-width: 70px; text-align: right; }
  .up { color: #22c55e; }
  .down { color: #ef4444; }
  .bar-bg { height: 3px; background: #2a2d3a; border-radius: 2px;
            margin-top: 4px; width: 100%; }
  .bar-fill { height: 3px; border-radius: 2px; }
  .loading { text-align: center; padding: 60px 20px; color: #555; font-size: 14px; }
  .updated { font-size: 11px; color: #555; text-align: center;
             padding: 16px 0 4px; }
  .market-summary { display: flex; gap: 8px; padding: 12px 16px; }
  .summary-card { flex: 1; background: #1a1d27; border-radius: 10px;
                  border: 1px solid #2a2d3a; padding: 10px 12px; }
  .summary-label { font-size: 11px; color: #666; }
  .summary-value { font-size: 18px; font-weight: 700; margin-top: 2px; }
  .summary-sub { font-size: 11px; color: #555; margin-top: 2px; }
  @media (prefers-color-scheme: light) {
    body { background: #f5f5f7; color: #1d1d1f; }
    .header { background: #fff; border-color: #e5e5ea; }
    .tab { background: #f5f5f7; color: #999; border-color: #e5e5ea; }
    .tab.active { background: #fff; color: #1d1d1f; }
    .card, .summary-card { background: #fff; border-color: #e5e5ea; }
    .stock-row { border-color: #f0f0f0; }
    .bar-bg { background: #e5e5ea; }
  }
</style>
</head>
<body>
<div class="header">
  <h1>📈 시장 주도 종목 <button class="refresh-btn" onclick="loadData()">새로고침</button></h1>
  <div class="date" id="dateLabel">데이터 불러오는 중...</div>
</div>

<div class="market-summary" id="summaryArea"></div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('kospi',this)">코스피</div>
  <div class="tab" onclick="switchTab('nasdaq',this)">나스닥</div>
</div>

<div class="content">
  <div id="kospi-pane">
    <div class="section">
      <div class="section-title"><span class="dot-up"></span>상위 상승</div>
      <div class="card" id="kospi-up"><div class="loading">불러오는 중...</div></div>
    </div>
    <div class="section">
      <div class="section-title"><span class="dot-down"></span>상위 하락</div>
      <div class="card" id="kospi-down"><div class="loading">불러오는 중...</div></div>
    </div>
  </div>
  <div id="nasdaq-pane" style="display:none">
    <div class="section">
      <div class="section-title"><span class="dot-up"></span>상위 상승</div>
      <div class="card" id="nasdaq-up"><div class="loading">불러오는 중...</div></div>
    </div>
    <div class="section">
      <div class="section-title"><span class="dot-down"></span>상위 하락</div>
      <div class="card" id="nasdaq-down"><div class="loading">불러오는 중...</div></div>
    </div>
  </div>
  <div class="updated" id="updatedAt"></div>
</div>

<script>
let data = null;

function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('kospi-pane').style.display = name==='kospi' ? '' : 'none';
  document.getElementById('nasdaq-pane').style.display = name==='nasdaq' ? '' : 'none';
}

function maxAbs(arr) {
  return Math.max(...arr.map(s => Math.abs(s.chg_pct)), 1);
}

function renderStocks(elId, stocks, isUp) {
  const el = document.getElementById(elId);
  if (!stocks || !stocks.length) { el.innerHTML = '<div class="loading">데이터 없음</div>'; return; }
  const max = maxAbs(stocks);
  el.innerHTML = stocks.map((s, i) => {
    const cls = isUp ? 'up' : 'down';
    const sign = isUp ? '+' : '';
    const pct = Math.abs(s.chg_pct) / max * 100;
    const price = typeof s.종가 !== 'undefined'
      ? Number(s.종가).toLocaleString()
      : (s.close ? Number(s.close).toLocaleString() : '');
    const name = s.종목 || s.ticker || s.종목명 || '';
    return `<div class="stock-row">
      <div class="rank">${i+1}</div>
      <div style="flex:1">
        <div class="name">${name}</div>
        <div class="bar-bg"><div class="bar-fill ${cls}" style="width:${pct}%;background:${isUp?'#22c55e':'#ef4444'}"></div></div>
      </div>
      <div class="price">${price}</div>
      <div class="change ${cls}">${sign}${s.chg_pct || s.등락률}%</div>
    </div>`;
  }).join('');
}

function renderSummary(d) {
  const area = document.getElementById('summaryArea');
  if (!d) return;
  area.innerHTML = `
    <div class="summary-card">
      <div class="summary-label">코스피 날짜</div>
      <div class="summary-value" style="font-size:14px">${d.date || '-'}</div>
      <div class="summary-sub">상승 ${d.kospi_up_cnt||0} · 하락 ${d.kospi_down_cnt||0}</div>
    </div>
    <div class="summary-card">
      <div class="summary-label">나스닥 날짜</div>
      <div class="summary-value" style="font-size:14px">${d.date || '-'}</div>
      <div class="summary-sub">상승 ${d.nasdaq_up_cnt||0} · 하락 ${d.nasdaq_down_cnt||0}</div>
    </div>`;
}

async function loadData() {
  document.getElementById('dateLabel').textContent = '데이터 불러오는 중...';
  try {
    const res = await fetch('/api/data');
    data = await res.json();
    document.getElementById('dateLabel').textContent = `📅 ${data.date || ''} 기준`;
    document.getElementById('updatedAt').textContent = `마지막 업데이트: ${data.updated_at || ''}`;
    renderSummary(data);
    renderStocks('kospi-up',   data.kospi_up,    true);
    renderStocks('kospi-down', data.kospi_down,  false);
    renderStocks('nasdaq-up',  data.nasdaq_up,   true);
    renderStocks('nasdaq-down',data.nasdaq_down, false);
  } catch(e) {
    document.getElementById('dateLabel').textContent = '❌ 데이터 로드 실패';
  }
}

loadData();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "데이터 없음. fetch_data.py를 먼저 실행하세요."}), 404

@app.route("/api/refresh", methods=["POST"])
def refresh():
    os.system("python fetch_data.py")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
