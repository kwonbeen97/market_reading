"""
데이터 수집 스크립트 - GitHub Actions가 매일 자동 실행
또는 수동으로: python fetch_data.py
"""
import pandas as pd
import yfinance as yf
import json, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 10

today = datetime.today()
if today.weekday() == 0:
    TARGET = today - timedelta(days=3)
elif today.weekday() == 6:
    TARGET = today - timedelta(days=2)
else:
    TARGET = today - timedelta(days=1)
TARGET_DATE = TARGET.strftime("%Y-%m-%d")

KOSPI_TICKERS = [
    ("005930.KS","삼성전자"),("000660.KS","SK하이닉스"),("207940.KS","삼성바이오"),
    ("005490.KS","POSCO홀딩스"),("035420.KS","NAVER"),("000270.KS","기아"),
    ("005380.KS","현대차"),("051910.KS","LG화학"),("006400.KS","삼성SDI"),
    ("035720.KS","카카오"),("066570.KS","LG전자"),("012330.KS","현대모비스"),
    ("028260.KS","삼성물산"),("017670.KS","SK텔레콤"),("030200.KS","KT"),
    ("055550.KS","신한지주"),("105560.KS","KB금융"),("086790.KS","하나금융"),
    ("032830.KS","삼성생명"),("003490.KS","대한항공"),("329180.KS","현대중공업"),
    ("010140.KS","삼성중공업"),("042660.KS","한화오션"),("012450.KS","한화에어로"),
    ("247540.KS","에코프로비엠"),("086520.KS","에코프로"),("373220.KS","LG에너지솔루션"),
    ("259960.KS","크래프톤"),("352820.KS","하이브"),("000100.KS","유한양행"),
    ("009150.KS","삼성전기"),("018260.KS","삼성SDS"),("096770.KS","SK이노베이션"),
    ("003550.KS","LG"),("011200.KS","HMM"),("034020.KS","두산에너빌리티"),
    ("316140.KS","우리금융"),("041510.KS","에스엠"),("010950.KS","S-Oil"),
    ("047050.KS","포스코인터"),
]

NASDAQ_TICKERS = [
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","COST",
    "AMD","NFLX","QCOM","ADBE","INTU","CSCO","TXN","AMGN","ISRG",
    "BKNG","VRTX","REGN","GILD","PANW","ADI","LRCX","KLAC","MRVL",
    "CDNS","SNPS","ORLY","MNST","PCAR","CTAS","MELI","ADP","PAYX",
    "FTNT","CPRT","ROST","DXCM","ODFL","IDXX","CRWD","ZS","DDOG",
    "NET","COIN","PLTR","SMCI","ARM","MU","AMAT","MCHP","INTC","NXPI",
    "ON","ENPH","FSLR","MRNA","ILMN",
]

def get_leaders(tickers_input, is_kospi=False):
    if is_kospi:
        tickers = [t for t, _ in tickers_input]
        name_map = {t: n for t, n in tickers_input}
    else:
        tickers = tickers_input
        name_map = {t: t for t in tickers}

    end   = TARGET + timedelta(days=1)
    start = TARGET - timedelta(days=7)
    rows  = []

    for ticker in tickers:
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
            rows.append({
                "종목"   : name_map.get(ticker, ticker),
                "티커"   : ticker,
                "종가"   : round(close, 2),
                "chg_pct": chg_pct,
            })
        except:
            continue

    if not rows:
        return [], []
    df_r = pd.DataFrame(rows).sort_values("chg_pct", ascending=False)
    return df_r.head(TOP_N).to_dict("records"), df_r.tail(TOP_N).iloc[::-1].to_dict("records")

print(f"[데이터 수집] {TARGET_DATE}")
print("코스피 수집 중...")
k_up, k_down = get_leaders(KOSPI_TICKERS, is_kospi=True)
print("나스닥 수집 중...")
n_up, n_down = get_leaders(NASDAQ_TICKERS, is_kospi=False)

result = {
    "date"          : TARGET_DATE,
    "updated_at"    : datetime.now().strftime("%Y-%m-%d %H:%M"),
    "kospi_up"      : k_up,
    "kospi_down"    : k_down,
    "nasdaq_up"     : n_up,
    "nasdaq_down"   : n_down,
    "kospi_up_cnt"  : len(k_up),
    "kospi_down_cnt": len(k_down),
    "nasdaq_up_cnt" : len(n_up),
    "nasdaq_down_cnt": len(n_down),
}

with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 완료! market_data.json 저장됨")
