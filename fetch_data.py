"""
데이터 수집 스크립트 v3 - 섹터 분류 + 시가총액 상위 대형주
"""
import pandas as pd
import yfinance as yf
import json, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 15

today = datetime.today()
if today.weekday() == 0:
    TARGET = today - timedelta(days=3)
elif today.weekday() == 6:
    TARGET = today - timedelta(days=2)
else:
    TARGET = today - timedelta(days=1)
TARGET_DATE = TARGET.strftime("%Y-%m-%d")

# ── 코스피 대형주 (섹터 포함) ─────────────────────────────────
KOSPI_TICKERS = [
    # 반도체
    ("000660.KS","SK하이닉스","반도체"),
    ("005930.KS","삼성전자","반도체"),
    ("009150.KS","삼성전기","반도체"),
    ("058470.KS","리노공업","반도체"),
    ("042700.KS","한미반도체","반도체"),
    # 전력/에너지
    ("012450.KS","한화에어로스페이스","전력/방산"),
    ("034020.KS","두산에너빌리티","전력/방산"),
    ("015760.KS","한국전력","전력/방산"),
    ("047050.KS","포스코인터내셔널","전력/방산"),
    ("267260.KS","현대일렉트릭","전력/방산"),
    # 이차전지
    ("373220.KS","LG에너지솔루션","이차전지"),
    ("006400.KS","삼성SDI","이차전지"),
    ("051910.KS","LG화학","이차전지"),
    ("247540.KS","에코프로비엠","이차전지"),
    ("086520.KS","에코프로","이차전지"),
    # 바이오/제약
    ("207940.KS","삼성바이오로직스","바이오"),
    ("068270.KS","셀트리온","바이오"),
    ("000100.KS","유한양행","바이오"),
    ("128940.KS","한미약품","바이오"),
    ("096530.KS","씨젠","바이오"),
    # 자동차
    ("005380.KS","현대차","자동차"),
    ("000270.KS","기아","자동차"),
    ("012330.KS","현대모비스","자동차"),
    ("011210.KS","현대위아","자동차"),
    ("018880.KS","한온시스템","자동차"),
    # IT/플랫폼
    ("035420.KS","NAVER","IT/플랫폼"),
    ("035720.KS","카카오","IT/플랫폼"),
    ("259960.KS","크래프톤","IT/플랫폼"),
    ("018260.KS","삼성SDS","IT/플랫폼"),
    ("066570.KS","LG전자","IT/플랫폼"),
    # 금융
    ("105560.KS","KB금융","금융"),
    ("055550.KS","신한지주","금융"),
    ("086790.KS","하나금융","금융"),
    ("316140.KS","우리금융","금융"),
    ("032830.KS","삼성생명","금융"),
    # 조선/중공업
    ("329180.KS","현대중공업","조선/중공업"),
    ("042660.KS","한화오션","조선/중공업"),
    ("010140.KS","삼성중공업","조선/중공업"),
    ("028260.KS","삼성물산","조선/중공업"),
    ("011200.KS","HMM","조선/중공업"),
    # 엔터/미디어
    ("352820.KS","하이브","엔터"),
    ("041510.KS","에스엠","엔터"),
    ("035900.KS","JYP엔터","엔터"),
    ("122870.KS","와이지엔터","엔터"),
    # 철강/소재
    ("005490.KS","POSCO홀딩스","철강/소재"),
    ("010950.KS","S-Oil","철강/소재"),
    ("003550.KS","LG","철강/소재"),
    ("017670.KS","SK텔레콤","철강/소재"),
    ("030200.KS","KT","철강/소재"),
]

# ── 나스닥 대형주 (섹터 포함) ─────────────────────────────────
NASDAQ_TICKERS = [
    # 반도체
    ("NVDA","NVIDIA","반도체"),
    ("AMD","AMD","반도체"),
    ("AVGO","Broadcom","반도체"),
    ("QCOM","Qualcomm","반도체"),
    ("AMAT","Applied Materials","반도체"),
    ("LRCX","Lam Research","반도체"),
    ("KLAC","KLA Corp","반도체"),
    ("MU","Micron","반도체"),
    ("MRVL","Marvell","반도체"),
    ("NXPI","NXP Semi","반도체"),
    # 빅테크
    ("AAPL","Apple","빅테크"),
    ("MSFT","Microsoft","빅테크"),
    ("GOOGL","Alphabet","빅테크"),
    ("AMZN","Amazon","빅테크"),
    ("META","Meta","빅테크"),
    # AI/소프트웨어
    ("PLTR","Palantir","AI/소프트웨어"),
    ("CRWD","CrowdStrike","AI/소프트웨어"),
    ("PANW","Palo Alto","AI/소프트웨어"),
    ("DDOG","Datadog","AI/소프트웨어"),
    ("ZS","Zscaler","AI/소프트웨어"),
    ("NET","Cloudflare","AI/소프트웨어"),
    ("ADBE","Adobe","AI/소프트웨어"),
    ("INTU","Intuit","AI/소프트웨어"),
    ("CDNS","Cadence","AI/소프트웨어"),
    ("SNPS","Synopsys","AI/소프트웨어"),
    # 전기차/에너지
    ("TSLA","Tesla","전기차/에너지"),
    ("ENPH","Enphase","전기차/에너지"),
    ("FSLR","First Solar","전기차/에너지"),
    ("ON","ON Semi","전기차/에너지"),
    # 바이오/헬스
    ("AMGN","Amgen","바이오/헬스"),
    ("GILD","Gilead","바이오/헬스"),
    ("VRTX","Vertex","바이오/헬스"),
    ("REGN","Regeneron","바이오/헬스"),
    ("ISRG","Intuitive Surgical","바이오/헬스"),
    ("MRNA","Moderna","바이오/헬스"),
    ("IDXX","IDEXX Labs","바이오/헬스"),
    # 소비재/서비스
    ("COST","Costco","소비재/서비스"),
    ("SBUX","Starbucks","소비재/서비스"),
    ("ORLY","O'Reilly Auto","소비재/서비스"),
    ("MNST","Monster Beverage","소비재/서비스"),
    ("MELI","MercadoLibre","소비재/서비스"),
    # 금융/핀테크
    ("COIN","Coinbase","금융/핀테크"),
    ("SMCI","Super Micro","금융/핀테크"),
    ("ARM","Arm Holdings","금융/핀테크"),
    # 미디어/엔터
    ("NFLX","Netflix","미디어/엔터"),
    ("CSCO","Cisco","미디어/엔터"),
    ("TXN","Texas Instruments","미디어/엔터"),
    ("ADP","ADP","미디어/엔터"),
    ("PAYX","Paychex","미디어/엔터"),
]

def get_leaders(tickers_input):
    end   = TARGET + timedelta(days=1)
    start = TARGET - timedelta(days=7)
    rows  = []

    for ticker, name, sector in tickers_input:
        try:
            df = yf.download(ticker, start=start, end=end,
                             auto_adjust=True, progress=False)
            if df.empty or len(df) < 2:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            day = df[df.index.date == TARGET.date()]
            if day.empty:
                continue
            prev = df[df.index < day.index[0]]
            if prev.empty:
                continue
            prev_close = float(prev["Close"].iloc[-1])
            close      = float(day["Close"].iloc[0])
            chg_pct    = round((close - prev_close) / prev_close * 100, 2)
            volume     = int(day["Volume"].iloc[0])
            rows.append({
                "name"   : name,
                "ticker" : ticker,
                "sector" : sector,
                "close"  : round(close, 2),
                "chg_pct": chg_pct,
                "volume" : volume,
            })
        except:
            continue

    return rows

print(f"[데이터 수집] {TARGET_DATE}")
print("코스피 수집 중...")
kospi_rows = get_leaders(KOSPI_TICKERS)
print("나스닥 수집 중...")
nasdaq_rows = get_leaders(NASDAQ_TICKERS)

def top_n(rows, n, ascending=False):
    return sorted(rows, key=lambda x: x["chg_pct"], reverse=not ascending)[:n]

def by_sector(rows):
    sectors = {}
    for r in rows:
        s = r["sector"]
        if s not in sectors:
            sectors[s] = []
        sectors[s].append(r)
    # 섹터별 평균 등락률 계산
    result = []
    for s, stocks in sectors.items():
        avg = round(sum(x["chg_pct"] for x in stocks) / len(stocks), 2)
        result.append({
            "sector": s,
            "avg_chg": avg,
            "stocks": sorted(stocks, key=lambda x: x["chg_pct"], reverse=True)
        })
    return sorted(result, key=lambda x: x["avg_chg"], reverse=True)

result = {
    "date"        : TARGET_DATE,
    "updated_at"  : datetime.now().strftime("%Y-%m-%d %H:%M"),
    "kospi_up"    : top_n(kospi_rows, TOP_N),
    "kospi_down"  : top_n(kospi_rows, TOP_N, ascending=True),
    "nasdaq_up"   : top_n(nasdaq_rows, TOP_N),
    "nasdaq_down" : top_n(nasdaq_rows, TOP_N, ascending=True),
    "kospi_sectors" : by_sector(kospi_rows),
    "nasdaq_sectors": by_sector(nasdaq_rows),
}


with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 날짜별 히스토리 저장
import os
os.makedirs("history", exist_ok=True)
hist_path = f"history/{TARGET_DATE}.json"
with open(hist_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 완료! market_data.json + history/{TARGET_DATE}.json 저장됨")
