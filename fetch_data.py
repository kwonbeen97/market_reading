"""
데이터 수집 스크립트 - 코스피/나스닥 주도 종목 추출
"""
import pandas as pd
import yfinance as yf
import json, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 15

# ── 코스피 대형주 (섹터 직접 지정) ──────────────────────────
KOSPI_TICKERS = [
    ("000660.KS","SK하이닉스","반도체"),
    ("005930.KS","삼성전자","반도체"),
    ("009150.KS","삼성전기","반도체장비"),
    ("058470.KS","리노공업","반도체장비"),
    ("042700.KS","한미반도체","반도체장비"),
    ("012450.KS","한화에어로스페이스","방산/항공"),
    ("034020.KS","두산에너빌리티","에너지/발전"),
    ("015760.KS","한국전력","에너지/발전"),
    ("267260.KS","현대일렉트릭","전력기기"),
    ("047050.KS","포스코인터내셔널","무역/자원"),
    ("373220.KS","LG에너지솔루션","이차전지"),
    ("006400.KS","삼성SDI","이차전지"),
    ("051910.KS","LG화학","이차전지"),
    ("247540.KS","에코프로비엠","이차전지"),
    ("086520.KS","에코프로","이차전지"),
    ("207940.KS","삼성바이오로직스","바이오"),
    ("068270.KS","셀트리온","바이오"),
    ("000100.KS","유한양행","제약"),
    ("128940.KS","한미약품","제약"),
    ("096530.KS","씨젠","바이오"),
    ("005380.KS","현대차","자동차"),
    ("000270.KS","기아","자동차"),
    ("012330.KS","현대모비스","자동차부품"),
    ("011210.KS","현대위아","자동차부품"),
    ("018880.KS","한온시스템","자동차부품"),
    ("035420.KS","NAVER","IT플랫폼"),
    ("035720.KS","카카오","IT플랫폼"),
    ("259960.KS","크래프톤","게임/엔터"),
    ("018260.KS","삼성SDS","IT서비스"),
    ("066570.KS","LG전자","가전/전자"),
    ("105560.KS","KB금융","금융"),
    ("055550.KS","신한지주","금융"),
    ("086790.KS","하나금융","금융"),
    ("316140.KS","우리금융","금융"),
    ("032830.KS","삼성생명","보험"),
    ("329180.KS","현대중공업","조선"),
    ("042660.KS","한화오션","조선"),
    ("010140.KS","삼성중공업","조선"),
    ("028260.KS","삼성물산","건설/지주"),
    ("011200.KS","HMM","해운"),
    ("352820.KS","하이브","엔터"),
    ("041510.KS","에스엠","엔터"),
    ("035900.KS","JYP엔터","엔터"),
    ("122870.KS","와이지엔터","엔터"),
    ("005490.KS","POSCO홀딩스","철강"),
    ("010950.KS","S-Oil","정유"),
    ("003550.KS","LG","지주사"),
    ("017670.KS","SK텔레콤","통신"),
    ("030200.KS","KT","통신"),
]

# ── 나스닥 대형주 (섹터 직접 지정) ──────────────────────────
NASDAQ_TICKERS = [
    ("NVDA","NVIDIA","반도체"),
    ("AMD","AMD","반도체"),
    ("AVGO","Broadcom","반도체"),
    ("QCOM","Qualcomm","반도체"),
    ("AMAT","Applied Materials","반도체장비"),
    ("LRCX","Lam Research","반도체장비"),
    ("KLAC","KLA Corp","반도체장비"),
    ("MU","Micron","반도체"),
    ("MRVL","Marvell","반도체"),
    ("NXPI","NXP Semi","반도체"),
    ("AAPL","Apple","빅테크"),
    ("MSFT","Microsoft","빅테크"),
    ("GOOGL","Alphabet","빅테크"),
    ("AMZN","Amazon","빅테크"),
    ("META","Meta","빅테크"),
    ("PLTR","Palantir","AI/소프트웨어"),
    ("CRWD","CrowdStrike","사이버보안"),
    ("PANW","Palo Alto","사이버보안"),
    ("DDOG","Datadog","AI/소프트웨어"),
    ("ZS","Zscaler","사이버보안"),
    ("NET","Cloudflare","AI/소프트웨어"),
    ("ADBE","Adobe","소프트웨어"),
    ("INTU","Intuit","소프트웨어"),
    ("CDNS","Cadence","소프트웨어"),
    ("SNPS","Synopsys","소프트웨어"),
    ("TSLA","Tesla","전기차"),
    ("ENPH","Enphase","신재생에너지"),
    ("FSLR","First Solar","신재생에너지"),
    ("ON","ON Semi","반도체"),
    ("AMGN","Amgen","바이오"),
    ("GILD","Gilead","바이오"),
    ("VRTX","Vertex","바이오"),
    ("REGN","Regeneron","바이오"),
    ("ISRG","Intuitive Surgical","의료기기"),
    ("MRNA","Moderna","바이오"),
    ("IDXX","IDEXX Labs","의료기기"),
    ("COST","Costco","유통"),
    ("SBUX","Starbucks","소비재"),
    ("ORLY","O'Reilly Auto","소비재"),
    ("MNST","Monster Beverage","소비재"),
    ("MELI","MercadoLibre","이커머스"),
    ("COIN","Coinbase","핀테크"),
    ("SMCI","Super Micro","서버/AI인프라"),
    ("ARM","Arm Holdings","반도체"),
    ("NFLX","Netflix","미디어"),
    ("CSCO","Cisco","네트워크"),
    ("TXN","Texas Instruments","반도체"),
    ("ADP","ADP","HR/서비스"),
    ("PAYX","Paychex","HR/서비스"),
]

def find_last_trading_day():
    """실제 마지막 거래일 자동 탐색"""
    df = yf.download("005930.KS", period="10d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if not df.empty:
        return df.index[-1].date()
    d = datetime.today().date()
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d

TARGET_DATE_OBJ = find_last_trading_day()
TARGET = datetime.combine(TARGET_DATE_OBJ, datetime.min.time())
TARGET_DATE = TARGET_DATE_OBJ.strftime("%Y-%m-%d")
print(f"[데이터 수집] {TARGET_DATE}")

def get_leaders(tickers_input):
    end   = datetime.today()
    start = end - timedelta(days=10)
    rows  = []
    for ticker, name, sector in tickers_input:
        try:
            df = yf.download(ticker, start=start, end=end,
                             auto_adjust=True, progress=False)
            if df.empty or len(df) < 2:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=["Close"])
            if len(df) < 2:
                continue
            close      = float(df["Close"].iloc[-1])
            prev_close = float(df["Close"].iloc[-2])
            chg_pct    = round((close - prev_close) / prev_close * 100, 2)
            rows.append({
                "name"   : name,
                "ticker" : ticker,
                "sector" : sector,
                "close"  : round(close, 2),
                "chg_pct": chg_pct,
            })
        except:
            continue
    return rows

def top_n(rows, n, ascending=False):
    return sorted(rows, key=lambda x: x["chg_pct"], reverse=not ascending)[:n]

def by_sector(rows):
    sectors = {}
    for r in rows:
        s = r["sector"]
        if s not in sectors:
            sectors[s] = []
        sectors[s].append(r)
    result = []
    for s, stocks in sectors.items():
        avg = round(sum(x["chg_pct"] for x in stocks) / len(stocks), 2)
        result.append({
            "sector": s,
            "avg_chg": avg,
            "stocks": sorted(stocks, key=lambda x: x["chg_pct"], reverse=True)
        })
    return sorted(result, key=lambda x: x["avg_chg"], reverse=True)

# 코스피/나스닥 지수 수집
kospi_index = nasdaq_index = kospi_chg = nasdaq_chg = None
try:
    for sym, key in [("^KS11","kospi"),("^IXIC","nasdaq")]:
        df = yf.download(sym, period="5d", auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(subset=["Close"])
        if len(df) >= 2:
            c = round(float(df["Close"].iloc[-1]), 2)
            p = round(float(df["Close"].iloc[-2]), 2)
            chg = round((c-p)/p*100, 2)
            if key=="kospi": kospi_index,kospi_chg=c,chg
            else: nasdaq_index,nasdaq_chg=c,chg
    print(f"코스피: {kospi_index} ({kospi_chg}%), 나스닥: {nasdaq_index} ({nasdaq_chg}%)")
except Exception as e:
    print(f"지수 수집 실패: {e}")

# CNN Fear & Greed
fng_value = fng_label = fng_prev = None
try:
    import urllib.request
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.cnn.com"})
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
    fng_value = round(d["fear_and_greed"]["score"])
    fng_label = d["fear_and_greed"]["rating"]
    hist = d.get("fear_and_greed_historical",{}).get("data",[])
    if len(hist) >= 2:
        fng_prev = round(float(hist[-2]["y"]))
    print(f"CNN Fear & Greed: {fng_value} ({fng_label})")
except Exception as e:
    print(f"CNN FNG 수집 실패: {e}")

print("코스피 수집 중...")
kospi_rows = get_leaders(KOSPI_TICKERS)
print("나스닥 수집 중...")
nasdaq_rows = get_leaders(NASDAQ_TICKERS)

result = {
    "date"         : TARGET_DATE,
    "updated_at"   : datetime.now().strftime("%Y-%m-%d %H:%M"),
    "fng"          : fng_value,
    "fng_label"    : fng_label,
    "fng_prev"     : fng_prev,
    "kospi_index"  : kospi_index,
    "kospi_chg"    : kospi_chg,
    "nasdaq_index" : nasdaq_index,
    "nasdaq_chg"   : nasdaq_chg,
    "kospi_up"     : top_n(kospi_rows, TOP_N),
    "kospi_down"   : top_n(kospi_rows, TOP_N, ascending=True),
    "nasdaq_up"    : top_n(nasdaq_rows, TOP_N),
    "nasdaq_down"  : top_n(nasdaq_rows, TOP_N, ascending=True),
    "kospi_sectors": by_sector(kospi_rows),
    "nasdaq_sectors": by_sector(nasdaq_rows),
}

with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

os.makedirs("history", exist_ok=True)
with open(f"history/{TARGET_DATE}.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 완료! market_data.json + history/{TARGET_DATE}.json 저장됨")
