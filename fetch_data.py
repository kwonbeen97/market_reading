"""
데이터 수집 스크립트 v3 - 섹터 분류 + 시가총액 상위 대형주
"""
import pandas as pd
import yfinance as yf
import json, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 15

# ── 섹터 영→한 매핑 ──────────────────────────────────────────
SECTOR_MAP = {
    "Technology": "IT/기술",
    "Semiconductors": "반도체",
    "Semiconductor Equipment & Materials": "반도체장비",
    "Consumer Electronics": "IT/기술",
    "Software": "소프트웨어",
    "Software—Application": "소프트웨어",
    "Software—Infrastructure": "소프트웨어",
    "Internet Content & Information": "IT플랫폼",
    "Communication Services": "통신/미디어",
    "Telecom Services": "통신",
    "Entertainment": "엔터",
    "Electronic Gaming & Multimedia": "엔터",
    "Health Care": "바이오/헬스",
    "Healthcare": "바이오/헬스",
    "Biotechnology": "바이오",
    "Drug Manufacturers—General": "제약",
    "Drug Manufacturers—Specialty & Generic": "제약",
    "Medical Devices": "의료기기",
    "Diagnostics & Research": "바이오/헬스",
    "Consumer Discretionary": "소비재",
    "Auto Manufacturers": "자동차",
    "Auto Parts": "자동차부품",
    "Specialty Retail": "소비재",
    "Restaurants": "소비재",
    "Beverages—Non-Alcoholic": "소비재",
    "Discount Stores": "유통",
    "Internet Retail": "이커머스",
    "Financials": "금융",
    "Financial Services": "금융",
    "Banks": "은행",
    "Insurance": "보험",
    "Capital Markets": "금융",
    "Industrials": "산업재",
    "Aerospace & Defense": "방산/항공",
    "Specialty Industrial Machinery": "기계/장비",
    "Electrical Equipment & Parts": "전력/전기",
    "Marine Shipping": "해운",
    "Staffing & Employment Services": "서비스",
    "Business Services": "서비스",
    "Energy": "에너지",
    "Oil & Gas Refining & Marketing": "정유",
    "Oil & Gas Integrated": "에너지",
    "Utilities": "유틸리티",
    "Utilities—Regulated Electric": "전력",
    "Materials": "소재/철강",
    "Steel": "철강",
    "Chemicals": "화학",
    "Basic Materials": "소재/철강",
    "Real Estate": "부동산",
}

SECTOR_FILE = "sectors.json"
_sector_cache = {}

def load_sector_cache():
    global _sector_cache
    if os.path.exists(SECTOR_FILE):
        with open(SECTOR_FILE, "r") as f:
            _sector_cache = json.load(f)
        print(f"섹터 캐시 로드: {len(_sector_cache)}개")

def save_sector_cache():
    with open(SECTOR_FILE, "w") as f:
        json.dump(_sector_cache, f)

def prefetch_sectors(tickers):
    missing = [t for t in tickers if t not in _sector_cache]
    if not missing:
        print(f"섹터 캐시 사용 ({len(_sector_cache)}개)")
        return
    print(f"새 섹터 수집: {len(missing)}개")
    for ticker in missing:
        try:
            info = yf.Ticker(ticker).info
            raw = info.get("industry") or info.get("sector") or ""
            mapped = SECTOR_MAP.get(raw, raw[:6] if raw else "기타")
            _sector_cache[ticker] = mapped
            print(f"  {ticker}: {mapped}")
        except:
            _sector_cache[ticker] = "기타"
    save_sector_cache()

def get_sector(ticker):
    return _sector_cache.get(ticker, "기타")

load_sector_cache()


today = datetime.today()

# 가장 최근 거래일 자동 탐색 (최대 7일 전까지)
def find_last_trading_day():
    import yfinance as _yf
    df = _yf.download("005930.KS", period="7d", auto_adjust=True, progress=False)
    if isinstance(df.columns, __import__('pandas').MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if not df.empty:
        return df.index[-1].date()
    # fallback
    d = today - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.date()

TARGET_DATE_OBJ = find_last_trading_day()
TARGET = datetime.combine(TARGET_DATE_OBJ, datetime.min.time())
print(f"최근 거래일: {TARGET_DATE_OBJ}")
TARGET_DATE = TARGET.strftime("%Y-%m-%d")

# ── 코스피 대형주 티커 + 이름 (섹터는 yfinance 자동) ─────────
KOSPI_RAW = [
    ("000660.KS","SK하이닉스"),("005930.KS","삼성전자"),("009150.KS","삼성전기"),
    ("058470.KS","리노공업"),("042700.KS","한미반도체"),("012450.KS","한화에어로스페이스"),
    ("034020.KS","두산에너빌리티"),("015760.KS","한국전력"),("047050.KS","포스코인터내셔널"),
    ("267260.KS","현대일렉트릭"),("373220.KS","LG에너지솔루션"),("006400.KS","삼성SDI"),
    ("051910.KS","LG화학"),("247540.KS","에코프로비엠"),("086520.KS","에코프로"),
    ("207940.KS","삼성바이오로직스"),("068270.KS","셀트리온"),("000100.KS","유한양행"),
    ("128940.KS","한미약품"),("096530.KS","씨젠"),("005380.KS","현대차"),
    ("000270.KS","기아"),("012330.KS","현대모비스"),("011210.KS","현대위아"),
    ("018880.KS","한온시스템"),("035420.KS","NAVER"),("035720.KS","카카오"),
    ("259960.KS","크래프톤"),("018260.KS","삼성SDS"),("066570.KS","LG전자"),
    ("105560.KS","KB금융"),("055550.KS","신한지주"),("086790.KS","하나금융"),
    ("316140.KS","우리금융"),("032830.KS","삼성생명"),("329180.KS","현대중공업"),
    ("042660.KS","한화오션"),("010140.KS","삼성중공업"),("028260.KS","삼성물산"),
    ("011200.KS","HMM"),("352820.KS","하이브"),("041510.KS","에스엠"),
    ("035900.KS","JYP엔터"),("122870.KS","와이지엔터"),("005490.KS","POSCO홀딩스"),
    ("010950.KS","S-Oil"),("003550.KS","LG"),("017670.KS","SK텔레콤"),
    ("030200.KS","KT"),
]

# ── 나스닥 대형주 티커 + 이름 (섹터는 yfinance 자동) ──────────
NASDAQ_RAW = [
    ("NVDA","NVIDIA"),("AMD","AMD"),("AVGO","Broadcom"),("QCOM","Qualcomm"),
    ("AMAT","Applied Materials"),("LRCX","Lam Research"),("KLAC","KLA Corp"),
    ("MU","Micron"),("MRVL","Marvell"),("NXPI","NXP Semi"),
    ("AAPL","Apple"),("MSFT","Microsoft"),("GOOGL","Alphabet"),
    ("AMZN","Amazon"),("META","Meta"),("PLTR","Palantir"),
    ("CRWD","CrowdStrike"),("PANW","Palo Alto"),("DDOG","Datadog"),
    ("ZS","Zscaler"),("NET","Cloudflare"),("ADBE","Adobe"),
    ("INTU","Intuit"),("CDNS","Cadence"),("SNPS","Synopsys"),
    ("TSLA","Tesla"),("ENPH","Enphase"),("FSLR","First Solar"),("ON","ON Semi"),
    ("AMGN","Amgen"),("GILD","Gilead"),("VRTX","Vertex"),("REGN","Regeneron"),
    ("ISRG","Intuitive Surgical"),("MRNA","Moderna"),("IDXX","IDEXX Labs"),
    ("COST","Costco"),("SBUX","Starbucks"),("ORLY","O'Reilly Auto"),
    ("MNST","Monster Beverage"),("MELI","MercadoLibre"),
    ("COIN","Coinbase"),("SMCI","Super Micro"),("ARM","Arm Holdings"),
    ("NFLX","Netflix"),("CSCO","Cisco"),("TXN","Texas Instruments"),
    ("ADP","ADP"),("PAYX","Paychex"),
]

def get_leaders(raw_list):
    end   = TARGET + timedelta(days=1)
    start = TARGET - timedelta(days=7)
    rows  = []

    for ticker, name in raw_list:
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

# 코스피/나스닥 지수 수집
kospi_index = None
kospi_chg   = None
nasdaq_index = None
nasdaq_chg   = None
try:
    import yfinance as _yf
    for sym, key in [("^KS11","kospi"),("^IXIC","nasdaq")]:
        _df = _yf.download(sym, start=TARGET-timedelta(days=7), end=TARGET+timedelta(days=1),
                           auto_adjust=True, progress=False)
        if isinstance(_df.columns, __import__('pandas').MultiIndex):
            _df.columns = _df.columns.get_level_values(0)
        _day = _df[_df.index.date == TARGET.date()]
        if not _day.empty:
            _prev = _df[_df.index < _day.index[0]]
            _c = float(_day["Close"].iloc[0])
            _p = float(_prev["Close"].iloc[-1]) if not _prev.empty else _c
            _chg = round((_c - _p) / _p * 100, 2)
            if key == "kospi":
                kospi_index = round(_c, 2)
                kospi_chg   = _chg
            else:
                nasdaq_index = round(_c, 2)
                nasdaq_chg   = _chg
    print(f"코스피: {kospi_index} ({kospi_chg}%), 나스닥: {nasdaq_index} ({nasdaq_chg}%)")
except Exception as e:
    print(f"지수 수집 실패: {e}")
print("코스피 섹터 사전 수집 중...")
prefetch_sectors([t for t,_ in KOSPI_RAW])
print("코스피 수집 중...")
kospi_rows = get_leaders(KOSPI_RAW)
print("나스닥 섹터 사전 수집 중...")
prefetch_sectors([t for t,_ in NASDAQ_RAW])
print("나스닥 수집 중...")
nasdaq_rows = get_leaders(NASDAQ_RAW)

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

# CNN Fear & Greed 수집
fng_value = None
fng_label = None
fng_prev  = None
try:
    import urllib.request as _ur
    _url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    _req = _ur.Request(_url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.cnn.com"})
    with _ur.urlopen(_req, timeout=8) as _r:
        _d = json.loads(_r.read())
    fng_value = round(_d["fear_and_greed"]["score"])
    fng_label = _d["fear_and_greed"]["rating"]
    # previous close
    hist = _d.get("fear_and_greed_historical", {}).get("data", [])
    if len(hist) >= 2:
        fng_prev = round(float(hist[-2]["y"]))
    print(f"CNN Fear & Greed: {fng_value} ({fng_label})")
except Exception as e:
    print(f"CNN FNG 수집 실패: {e}")

result = {
    "date"        : TARGET_DATE,
    "updated_at"  : datetime.now().strftime("%Y-%m-%d %H:%M"),
    "fng"         : fng_value,
    "fng_label"   : fng_label,
    "fng_prev"    : fng_prev,
    "kospi_index" : kospi_index,
    "kospi_chg"   : kospi_chg,
    "nasdaq_index": nasdaq_index,
    "nasdaq_chg"  : nasdaq_chg,
    "fng_label"   : fng_label,
    "fng_prev"    : fng_prev,
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
