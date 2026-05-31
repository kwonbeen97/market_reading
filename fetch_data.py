"""
데이터 수집 스크립트 - 코스피200 + 나스닥100
"""
import pandas as pd
import yfinance as yf
import json, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 15

# ── 코스피 200 (섹터 직접 지정) ──────────────────────────────
KOSPI_TICKERS = [
    # 반도체
    ("005930.KS","삼성전자","반도체"),
    ("000660.KS","SK하이닉스","반도체"),
    ("009150.KS","삼성전기","반도체"),
    ("042700.KS","한미반도체","반도체"),
    ("058470.KS","리노공업","반도체"),
    ("036830.KS","솔브레인홀딩스","반도체"),
    ("357780.KS","솔브레인","반도체"),
    ("240810.KS","원익IPS","반도체"),
    ("036490.KS","SK머티리얼즈","반도체"),
    ("140860.KS","파크시스템스","반도체"),
    # 이차전지
    ("373220.KS","LG에너지솔루션","이차전지"),
    ("006400.KS","삼성SDI","이차전지"),
    ("051910.KS","LG화학","이차전지"),
    ("247540.KS","에코프로비엠","이차전지"),
    ("086520.KS","에코프로","이차전지"),
    ("096770.KS","SK이노베이션","이차전지"),
    ("003670.KS","포스코퓨처엠","이차전지"),
    ("298050.KS","효성첨단소재","이차전지"),
    ("456040.KS","OCI홀딩스","이차전지"),
    ("272450.KS","배터리솔루션","이차전지"),
    # 바이오/제약
    ("207940.KS","삼성바이오로직스","바이오"),
    ("068270.KS","셀트리온","바이오"),
    ("000100.KS","유한양행","제약"),
    ("128940.KS","한미약품","제약"),
    ("096530.KS","씨젠","바이오"),
    ("326030.KS","SK바이오팜","바이오"),
    ("145020.KS","휴젤","바이오"),
    ("196170.KS","알테오젠","바이오"),
    ("009420.KS","한올바이오파마","제약"),
    ("185750.KS","종근당","제약"),
    ("000220.KS","유유제약","제약"),
    ("064550.KS","바이오니아","바이오"),
    # 자동차
    ("005380.KS","현대차","자동차"),
    ("000270.KS","기아","자동차"),
    ("012330.KS","현대모비스","자동차부품"),
    ("011210.KS","현대위아","자동차부품"),
    ("018880.KS","한온시스템","자동차부품"),
    ("204320.KS","만도","자동차부품"),
    ("007340.KS","LS전선아시아","자동차부품"),
    ("023810.KS","인팩","자동차부품"),
    # IT/플랫폼
    ("035420.KS","NAVER","IT플랫폼"),
    ("035720.KS","카카오","IT플랫폼"),
    ("018260.KS","삼성SDS","IT서비스"),
    ("066570.KS","LG전자","가전/전자"),
    ("034220.KS","LG디스플레이","디스플레이"),
    ("030200.KS","KT","통신"),
    ("017670.KS","SK텔레콤","통신"),
    ("032640.KS","LG유플러스","통신"),
    ("259960.KS","크래프톤","게임"),
    ("036570.KS","엔씨소프트","게임"),
    ("251270.KS","넷마블","게임"),
    ("263750.KS","펄어비스","게임"),
    # 금융/보험
    ("105560.KS","KB금융","금융"),
    ("055550.KS","신한지주","금융"),
    ("086790.KS","하나금융","금융"),
    ("316140.KS","우리금융","금융"),
    ("024110.KS","기업은행","금융"),
    ("138930.KS","BNK금융","금융"),
    ("139130.KS","DGB금융","금융"),
    ("032830.KS","삼성생명","보험"),
    ("000810.KS","삼성화재","보험"),
    ("000060.KS","메리츠화재","보험"),
    ("005830.KS","DB손보","보험"),
    ("082640.KS","동양생명","보험"),
    # 조선/해운
    ("329180.KS","현대중공업","조선"),
    ("042660.KS","한화오션","조선"),
    ("010140.KS","삼성중공업","조선"),
    ("267250.KS","HD현대","조선/지주"),
    ("009540.KS","HD한국조선해양","조선"),
    ("011200.KS","HMM","해운"),
    ("003490.KS","대한항공","항공"),
    ("020560.KS","아시아나항공","항공"),
    # 방산/에너지
    ("012450.KS","한화에어로스페이스","방산"),
    ("047050.KS","포스코인터내셔널","방산/무역"),
    ("034020.KS","두산에너빌리티","에너지/발전"),
    ("015760.KS","한국전력","에너지/발전"),
    ("267260.KS","현대일렉트릭","전력기기"),
    ("028050.KS","삼성중공업우","에너지"),
    ("010690.KS","화신","방산"),
    # 철강/소재
    ("005490.KS","POSCO홀딩스","철강"),
    ("010130.KS","고려아연","비철금속"),
    ("004020.KS","현대제철","철강"),
    ("006260.KS","LS","소재/지주"),
    ("011780.KS","금호석유","화학"),
    ("011170.KS","롯데케미칼","화학"),
    ("010950.KS","S-Oil","정유"),
    ("078930.KS","GS","에너지/지주"),
    ("096640.KS","한국가스공사","에너지"),
    ("071050.KS","한국금융지주","금융"),
    # 건설/부동산
    ("000720.KS","현대건설","건설"),
    ("028260.KS","삼성물산","건설/지주"),
    ("047040.KS","대우건설","건설"),
    ("000080.KS","하이트진로","음식료"),
    ("097950.KS","CJ제일제당","음식료"),
    ("004370.KS","농심","음식료"),
    ("271560.KS","오리온","음식료"),
    ("280360.KS","롯데웰푸드","음식료"),
    # 엔터/미디어
    ("352820.KS","하이브","엔터"),
    ("041510.KS","에스엠","엔터"),
    ("035900.KS","JYP엔터","엔터"),
    ("122870.KS","와이지엔터","엔터"),
    ("041960.KS","블리자드","엔터"),
    # 유통/서비스
    ("023530.KS","롯데쇼핑","유통"),
    ("069960.KS","현대백화점","유통"),
    ("004170.KS","신세계","유통"),
    ("282330.KS","BGF리테일","유통"),
    ("007070.KS","GS리테일","유통"),
    # 지주사
    ("003550.KS","LG","지주사"),
    ("034730.KS","SK","지주사"),
    ("000030.KS","우리은행","금융"),
    ("005940.KS","NH투자증권","증권"),
    ("016360.KS","삼성증권","증권"),
    ("071840.KS","롯데하이마트","유통"),
]

# ── 나스닥 100 (섹터 직접 지정) ──────────────────────────────
NASDAQ_TICKERS = [
    # 반도체 (한 섹터로 통합)
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
    ("ON","ON Semi","반도체"),
    ("MCHP","Microchip Tech","반도체"),
    ("ADI","Analog Devices","반도체"),
    ("TXN","Texas Instruments","반도체"),
    ("INTC","Intel","반도체"),
    ("ARM","Arm Holdings","반도체"),
    ("SNDK","SanDisk","반도체"),
    # 빅테크
    ("AAPL","Apple","빅테크"),
    ("MSFT","Microsoft","빅테크"),
    ("GOOGL","Alphabet","빅테크"),
    ("AMZN","Amazon","빅테크"),
    ("META","Meta","빅테크"),
    ("SMCI","Super Micro","빅테크"),
    # AI/소프트웨어 (사이버보안 통합)
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
    ("FTNT","Fortinet","AI/소프트웨어"),
    ("OKTA","Okta","AI/소프트웨어"),
    ("TEAM","Atlassian","AI/소프트웨어"),
    ("WDAY","Workday","AI/소프트웨어"),
    ("SNOW","Snowflake","AI/소프트웨어"),
    ("NOW","ServiceNow","AI/소프트웨어"),
    ("ANSS","ANSYS","AI/소프트웨어"),
    ("ZM","Zoom","AI/소프트웨어"),
    ("DOCU","DocuSign","AI/소프트웨어"),
    # 전기차/에너지
    ("TSLA","Tesla","전기차/에너지"),
    ("ENPH","Enphase","전기차/에너지"),
    ("FSLR","First Solar","전기차/에너지"),
    # 바이오/헬스
    ("AMGN","Amgen","바이오/헬스"),
    ("GILD","Gilead","바이오/헬스"),
    ("VRTX","Vertex","바이오/헬스"),
    ("REGN","Regeneron","바이오/헬스"),
    ("ISRG","Intuitive Surgical","바이오/헬스"),
    ("MRNA","Moderna","바이오/헬스"),
    ("IDXX","IDEXX Labs","바이오/헬스"),
    ("ILMN","Illumina","바이오/헬스"),
    ("BIIB","Biogen","바이오/헬스"),
    # 소비재/유통
    ("COST","Costco","소비재/유통"),
    ("SBUX","Starbucks","소비재/유통"),
    ("ORLY","O'Reilly Auto","소비재/유통"),
    ("MNST","Monster Beverage","소비재/유통"),
    ("MELI","MercadoLibre","소비재/유통"),
    ("DLTR","Dollar Tree","소비재/유통"),
    ("ROST","Ross Stores","소비재/유통"),
    ("CPRT","Copart","소비재/유통"),
    ("PEP","PepsiCo","소비재/유통"),
    ("MDLZ","Mondelez","소비재/유통"),
    ("KDP","Keurig Dr Pepper","소비재/유통"),
    ("EBAY","eBay","소비재/유통"),
    ("LULU","Lululemon","소비재/유통"),
    ("BKNG","Booking","소비재/유통"),
    ("ABNB","Airbnb","소비재/유통"),
    # 금융/핀테크
    ("COIN","Coinbase","금융/핀테크"),
    ("PYPL","PayPal","금융/핀테크"),
    ("ADP","ADP","금융/핀테크"),
    ("PAYX","Paychex","금융/핀테크"),
    ("VRSK","Verisk","금융/핀테크"),
    # 미디어/통신
    ("NFLX","Netflix","미디어/통신"),
    ("CSCO","Cisco","미디어/통신"),
    ("FAST","Fastenal","미디어/통신"),
    ("PCAR","PACCAR","미디어/통신"),
    ("ODFL","Old Dominion","미디어/통신"),
]

def find_last_trading_day():
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
TARGET_DATE = TARGET_DATE_OBJ.strftime("%Y-%m-%d")
print(f"[데이터 수집] {TARGET_DATE}")

def get_leaders(tickers_input):
    end   = datetime.today()
    start = end - timedelta(days=14)  # 연속일수 계산위해 더 길게
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

            # 거래량 급증 (오늘 거래량 vs 5일 평균)
            vol_today = float(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            vol_avg5  = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 and "Volume" in df.columns else vol_today
            vol_surge = round(vol_today / vol_avg5, 1) if vol_avg5 > 0 else 1.0

            # 연속 상승/하락 일수
            streak = 0
            closes = df["Close"].tolist()
            if len(closes) >= 2:
                direction = 1 if closes[-1] > closes[-2] else -1
                for i in range(len(closes)-1, 0, -1):
                    if (closes[i] > closes[i-1]) == (direction == 1):
                        streak += direction
                    else:
                        break

            rows.append({
                "name"     : name,
                "ticker"   : ticker,
                "sector"   : sector,
                "close"    : round(close, 2),
                "chg_pct"  : chg_pct,
                "vol_surge": vol_surge,
                "streak"   : streak,
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

# 코스피/나스닥 지수
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

print(f"코스피 수집 중... ({len(KOSPI_TICKERS)}개)")
kospi_rows = get_leaders(KOSPI_TICKERS)
print(f"나스닥 수집 중... ({len(NASDAQ_TICKERS)}개)")
nasdaq_rows = get_leaders(NASDAQ_TICKERS)
print(f"코스피 {len(kospi_rows)}개, 나스닥 {len(nasdaq_rows)}개 수집됨")

result = {
    "date"          : TARGET_DATE,
    "updated_at"    : datetime.now().strftime("%Y-%m-%d %H:%M"),
    "fng"           : fng_value,
    "fng_label"     : fng_label,
    "fng_prev"      : fng_prev,
    "kospi_index"   : kospi_index,
    "kospi_chg"     : kospi_chg,
    "nasdaq_index"  : nasdaq_index,
    "nasdaq_chg"    : nasdaq_chg,
    "kospi_up"      : top_n(kospi_rows, TOP_N),
    "kospi_down"    : top_n(kospi_rows, TOP_N, ascending=True),
    "nasdaq_up"     : top_n(nasdaq_rows, TOP_N),
    "nasdaq_down"   : top_n(nasdaq_rows, TOP_N, ascending=True),
    "kospi_sectors" : by_sector(kospi_rows),
    "nasdaq_sectors": by_sector(nasdaq_rows),
}

with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

os.makedirs("history", exist_ok=True)
with open(f"history/{TARGET_DATE}.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 완료! market_data.json + history/{TARGET_DATE}.json 저장됨")
