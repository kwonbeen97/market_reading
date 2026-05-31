from flask import Flask, jsonify, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "market_data.json"

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>시장 주도 종목</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f1117;color:#e8eaed;min-height:100vh}
.header{padding:16px 16px 0;border-bottom:1px solid #1e2235}
.header-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.header h1{font-size:18px;font-weight:700}
.date-badge{font-size:12px;color:#888;background:#1a1d27;padding:4px 10px;border-radius:20px;border:1px solid #2a2d3a}
.refresh-btn{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:7px 14px;font-size:13px;cursor:pointer;font-weight:600}
.tabs{display:flex;gap:0;border-bottom:1px solid #1e2235}
.tab{flex:1;padding:11px 8px;text-align:center;font-size:13px;font-weight:600;cursor:pointer;color:#666;border-bottom:2px solid transparent;transition:all .2s}
.tab.active{color:#e8eaed;border-bottom-color:#2563eb}
.view-tabs{display:flex;gap:6px;padding:12px 16px 0}
.view-tab{padding:6px 14px;font-size:12px;font-weight:600;border-radius:20px;cursor:pointer;border:1px solid #2a2d3a;background:#1a1d27;color:#888;transition:all .2s}
.view-tab.active{background:#2563eb;color:#fff;border-color:#2563eb}
.content{padding:12px 16px 24px}
/* 리스트 뷰 */
.section-label{font-size:11px;font-weight:700;letter-spacing:.8px;color:#555;margin:14px 0 6px;display:flex;align-items:center;gap:6px}
.dot{width:6px;height:6px;border-radius:50%}
.card{background:#1a1d27;border-radius:12px;border:1px solid #2a2d3a;overflow:hidden;margin-bottom:8px}
.stock-row{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid #1e2235}
.stock-row:last-child{border-bottom:none}
.rank{font-size:11px;color:#444;width:18px;flex-shrink:0}
.info{flex:1;min-width:0}
.name{font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sector-tag{display:inline-block;font-size:10px;padding:1px 6px;border-radius:4px;margin-top:2px;font-weight:600}
.bar-wrap{flex:1;margin:0 10px}
.bar-bg{height:3px;background:#2a2d3a;border-radius:2px}
.bar-fill{height:3px;border-radius:2px}
.price{font-size:12px;color:#666;margin-right:10px;white-space:nowrap}
.chg{font-size:14px;font-weight:700;min-width:64px;text-align:right;white-space:nowrap}
.up{color:#22c55e}.down{color:#ef4444}
/* 히트맵 */
.heatmap{display:grid;gap:4px;margin-top:8px}
.sector-block{background:#1a1d27;border-radius:10px;border:1px solid #2a2d3a;overflow:hidden}
.sector-header{padding:8px 12px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e2235}
.sector-name{font-size:12px;font-weight:700;color:#ccc}
.sector-avg{font-size:13px;font-weight:700}
.stocks-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:3px;padding:6px}
.heat-cell{border-radius:6px;padding:6px 8px;cursor:pointer;transition:opacity .15s;min-height:52px;display:flex;flex-direction:column;justify-content:space-between}
.heat-cell:hover{opacity:.8}
.heat-name{font-size:11px;font-weight:600;line-height:1.3;word-break:keep-all}
.heat-chg{font-size:13px;font-weight:700;margin-top:2px}
/* 색상 강도 */
.h-up-3{background:#14532d;color:#86efac}
.h-up-2{background:#166534;color:#bbf7d0}
.h-up-1{background:#15803d;color:#dcfce7}
.h-up-0{background:#1a3a28;color:#6ee7b7}
.h-dn-0{background:#3a1a1a;color:#fca5a5}
.h-dn-1{background:#7f1d1d;color:#fecaca}
.h-dn-2{background:#991b1b;color:#fee2e2}
.h-dn-3{background:#b91c1c;color:#fff}
.h-flat{background:#1e2235;color:#888}
.updated{text-align:center;font-size:11px;color:#444;padding:12px 0 4px}
</style>
</head>
<body>
<div class="header">
  <div class="header-top">
    <h1>📈 시장 주도 종목</h1>
    <button class="refresh-btn" onclick="loadData()">새로고침</button>
  </div>
  <div class="tabs">
    <div class="tab active" onclick="switchMarket('kospi',this)">코스피</div>
    <div class="tab" onclick="switchMarket('nasdaq',this)">나스닥</div>
  </div>
</div>

<div class="view-tabs">
  <div class="view-tab active" onclick="switchView('list',this)">순위</div>
  <div class="view-tab" onclick="switchView('heatmap',this)">히트맵</div>
</div>

<div class="content">
  <div id="list-view">
    <div class="section-label"><span class="dot" style="background:#22c55e"></span>상위 상승</div>
    <div class="card" id="up-list"></div>
    <div class="section-label"><span class="dot" style="background:#ef4444"></span>상위 하락</div>
    <div class="card" id="down-list"></div>
  </div>
  <div id="heatmap-view" style="display:none">
    <div class="heatmap" id="heatmap-grid"></div>
  </div>
  <div class="updated" id="updatedAt"></div>
</div>

<script>
let data=null, market='kospi', view='list';

function switchMarket(m,el){
  market=m;
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  render();
}
function switchView(v,el){
  view=v;
  document.querySelectorAll('.view-tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('list-view').style.display=v==='list'?'':'none';
  document.getElementById('heatmap-view').style.display=v==='heatmap'?'':'none';
  render();
}

const SECTOR_COLORS={
  '반도체':'#6366f1','이차전지':'#22c55e','바이오':'#ec4899',
  '전력/방산':'#f59e0b','자동차':'#14b8a6','IT/플랫폼':'#3b82f6',
  '금융':'#8b5cf6','조선/중공업':'#64748b','엔터':'#f43f5e',
  '철강/소재':'#78716c','빅테크':'#3b82f6','AI/소프트웨어':'#6366f1',
  '전기차/에너지':'#22c55e','바이오/헬스':'#ec4899','소비재/서비스':'#f59e0b',
  '금융/핀테크':'#8b5cf6','미디어/엔터':'#f43f5e',
};

function heatClass(v){
  if(v>5) return 'h-up-3';
  if(v>2) return 'h-up-2';
  if(v>0) return 'h-up-1';
  if(v>-0.5) return 'h-flat';
  if(v>-2) return 'h-dn-0';
  if(v>-5) return 'h-dn-1';
  return 'h-dn-3';
}

function renderList(){
  const up=data[market+'_up']||[], dn=data[market+'_down']||[];
  const max=Math.max(...[...up,...dn].map(s=>Math.abs(s.chg_pct)),1);
  function rows(arr,isUp){
    if(!arr.length) return '<div style="padding:14px;text-align:center;color:#444;font-size:13px">데이터 없음</div>';
    return arr.map((s,i)=>{
      const col=SECTOR_COLORS[s.sector]||'#666';
      const pct=Math.abs(s.chg_pct)/max*100;
      const sname=s.name||s.종목||s.ticker||'';
      const ssector=s.sector||s.섹터||'';
      const price=typeof s.close==='number'?s.close.toLocaleString():'';
      return `<div class="stock-row">
        <div class="rank">${i+1}</div>
        <div class="info">
          <div class="name">${sname}</div>
          <span class="sector-tag" ...>${ssector}</span>
        </div>
        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill" style="width:${pct}%;background:${isUp?'#22c55e':'#ef4444'}"></div></div></div>
        <div class="price">${price}</div>
        <div class="chg ${isUp?'up':'down'}">${isUp?'+':''}${s.chg_pct}%</div>
      </div>`;
    }).join('');
  }
  document.getElementById('up-list').innerHTML=rows(up,true);
  document.getElementById('down-list').innerHTML=rows(dn,false);
}

function renderHeatmap(){
  const sectors=data[market+'_sectors']||[];
  const grid=document.getElementById('heatmap-grid');
  if(!sectors.length){grid.innerHTML='<div style="padding:20px;text-align:center;color:#444">데이터 없음</div>';return;}
  grid.innerHTML=sectors.map(sec=>{
    const avgCls=sec.avg_chg>=0?'up':'down';
    const cells=sec.stocks.map(s=>`
      <div class="heat-cell ${heatClass(s.chg_pct)}" title="${s.name} ${s.chg_pct}%">
        <div class="heat-name">${s.name}</div>
        <div class="heat-chg">${s.chg_pct>0?'+':''}${s.chg_pct}%</div>
      </div>`).join('');
    return `<div class="sector-block">
      <div class="sector-header">
        <span class="sector-name">${sec.sector}</span>
        <span class="sector-avg ${avgCls}">${sec.avg_chg>0?'+':''}${sec.avg_chg}%</span>
      </div>
      <div class="stocks-grid">${cells}</div>
    </div>`;
  }).join('');
}

function render(){
  if(!data) return;
  if(view==='list') renderList();
  else renderHeatmap();
}

async function loadData(){
  try{
    const res=await fetch('/api/data');
    data=await res.json();
    document.getElementById('updatedAt').textContent='마지막 업데이트: '+(data.updated_at||'');
    render();
  }catch(e){
    document.getElementById('up-list').innerHTML='<div style="padding:14px;color:#ef4444;font-size:13px">데이터 로드 실패</div>';
  }
}
loadData();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "데이터 없음"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
