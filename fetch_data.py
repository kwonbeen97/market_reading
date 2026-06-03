"""
데이터 수집 스크립트 - 코스피200 + 나스닥100
"""
import pandas as pd
import yfinance as yf
import json, os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")

TOP_N = 15

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
    ("140860.KS","파크시스템스","반도체"),
    ("079550.KS","LIG넥스원","반도체"),
    ("217190.KS","브이원텍","반도체"),
    ("098460.KS","고영","반도체"),
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
    ("272110.KS","에코앤드림","이차전지"),
    ("064960.KS","SNT모티브","이차전지"),
    # 바이오/제약
    ("207940.KS","삼성바이오로직스","바이오/제약"),
    ("068270.KS","셀트리온","바이오/제약"),
    ("000100.KS","유한양행","바이오/제약"),
    ("128940.KS","한미약품","바이오/제약"),
    ("096530.KS","씨젠","바이오/제약"),
    ("326030.KS","SK바이오팜","바이오/제약"),
    ("145020.KS","휴젤","바이오/제약"),
    ("196170.KS","알테오젠","바이오/제약"),
    ("009420.KS","한올바이오파마","바이오/제약"),
    ("185750.KS","종근당","바이오/제약"),
    ("064550.KS","바이오니아","바이오/제약"),
    ("012200.KS","계양전기","바이오/제약"),
    ("302440.KS","SK바이오사이언스","바이오/제약"),
    ("950130.KS","엑세스바이오","바이오/제약"),
    ("141080.KS","리가켐바이오","바이오/제약"),
    ("311690.KS","오리엔트바이오","바이오/제약"),
    # 자동차/부품
    ("005380.KS","현대차","자동차/부품"),
    ("000270.KS","기아","자동차/부품"),
    ("012330.KS","현대모비스","자동차/부품"),
    ("011210.KS","현대위아","자동차/부품"),
    ("018880.KS","한온시스템","자동차/부품"),
    ("204320.KS","만도","자동차/부품"),
    ("000240.KS","한국타이어앤테크놀로지","자동차/부품"),
    ("161390.KS","한국타이어","자동차/부품"),
    ("073240.KS","금호타이어","자동차/부품"),
    ("010820.KS","에이치디씨","자동차/부품"),
    # IT/플랫폼
    ("035420.KS","NAVER","IT/플랫폼"),
    ("035720.KS","카카오","IT/플랫폼"),
    ("018260.KS","삼성SDS","IT/플랫폼"),
    ("066570.KS","LG전자","IT/플랫폼"),
    ("034220.KS","LG디스플레이","IT/플랫폼"),
    ("053800.KS","안랩","IT/플랫폼"),
    ("047560.KS","이스트소프트","IT/플랫폼"),
    ("950170.KS","카카오뱅크","IT/플랫폼"),
    ("293490.KS","카카오페이","IT/플랫폼"),
    # 게임/엔터
    ("259960.KS","크래프톤","게임/엔터"),
    ("036570.KS","엔씨소프트","게임/엔터"),
    ("251270.KS","넷마블","게임/엔터"),
    ("263750.KS","펄어비스","게임/엔터"),
    ("352820.KS","하이브","게임/엔터"),
    ("041510.KS","에스엠","게임/엔터"),
    ("035900.KS","JYP엔터","게임/엔터"),
    ("122870.KS","와이지엔터","게임/엔터"),
    ("225570.KS","넥슨게임즈","게임/엔터"),
    ("194480.KS","데브시스터즈","게임/엔터"),
    # 금융/보험
    ("105560.KS","KB금융","금융/보험"),
    ("055550.KS","신한지주","금융/보험"),
    ("086790.KS","하나금융","금융/보험"),
    ("316140.KS","우리금융","금융/보험"),
    ("024110.KS","기업은행","금융/보험"),
    ("138930.KS","BNK금융","금융/보험"),
    ("139130.KS","DGB금융","금융/보험"),
    ("032830.KS","삼성생명","금융/보험"),
    ("000810.KS","삼성화재","금융/보험"),
    ("005830.KS","DB손보","금융/보험"),
    ("082640.KS","동양생명","금융/보험"),
    ("071050.KS","한국금융지주","금융/보험"),
    ("005940.KS","NH투자증권","금융/보험"),
    ("016360.KS","삼성증권","금융/보험"),
    ("088350.KS","한화생명","금융/보험"),
    ("000370.KS","한화손해보험","금융/보험"),
    ("039490.KS","키움증권","금융/보험"),
    # 조선/해운/항공
    ("329180.KS","현대중공업","조선/해운/항공"),
    ("042660.KS","한화오션","조선/해운/항공"),
    ("010140.KS","삼성중공업","조선/해운/항공"),
    ("267250.KS","HD현대","조선/해운/항공"),
    ("009540.KS","HD한국조선해양","조선/해운/항공"),
    ("011200.KS","HMM","조선/해운/항공"),
    ("003490.KS","대한항공","조선/해운/항공"),
    ("020560.KS","아시아나항공","조선/해운/항공"),
    ("010620.KS","HD현대미포","조선/해운/항공"),
    ("000180.KS","성창기업지주","조선/해운/항공"),
    # 방산/전력
    ("012450.KS","한화에어로스페이스","방산/전력"),
    ("034020.KS","두산에너빌리티","방산/전력"),
    ("015760.KS","한국전력","방산/전력"),
    ("267260.KS","현대일렉트릭","방산/전력"),
    ("010120.KS","LS ELECTRIC","방산/전력"),
    ("298040.KS","효성중공업","방산/전력"),
    ("047810.KS","한국항공우주","방산/전력"),
    ("006360.KS","GS건설","방산/전력"),
    ("000030.KS","우리은행","방산/전력"),
    ("064350.KS","현대로템","방산/전력"),
    # 소재/에너지
    ("047050.KS","포스코인터내셔널","소재/에너지"),
    ("078930.KS","GS","소재/에너지"),
    ("010950.KS","S-Oil","소재/에너지"),
    ("096640.KS","한국가스공사","소재/에너지"),
    ("001040.KS","CJ","소재/에너지"),
    # 소재/철강/화학
    ("005490.KS","POSCO홀딩스","소재/철강/화학"),
    ("010130.KS","고려아연","소재/철강/화학"),
    ("004020.KS","현대제철","소재/철강/화학"),
    ("006260.KS","LS","소재/철강/화학"),
    ("011780.KS","금호석유","소재/철강/화학"),
    ("011170.KS","롯데케미칼","소재/철강/화학"),
    ("000120.KS","CJ대한통운","소재/철강/화학"),
    ("002380.KS","KCC","소재/철강/화학"),
    ("004490.KS","세방전지","소재/철강/화학"),
    # 통신/건설/유통
    ("030200.KS","KT","통신/건설/유통"),
    ("017670.KS","SK텔레콤","통신/건설/유통"),
    ("032640.KS","LG유플러스","통신/건설/유통"),
    ("000720.KS","현대건설","통신/건설/유통"),
    ("028260.KS","삼성물산","통신/건설/유통"),
    ("047040.KS","대우건설","통신/건설/유통"),
    ("023530.KS","롯데쇼핑","통신/건설/유통"),
    ("069960.KS","현대백화점","통신/건설/유통"),
    ("004170.KS","신세계","통신/건설/유통"),
    ("282330.KS","BGF리테일","통신/건설/유통"),
    ("000880.KS","한화","통신/건설/유통"),
    ("139480.KS","이마트","통신/건설/유통"),
    ("007070.KS","GS리테일","통신/건설/유통"),
    # 지주/기타
    ("003550.KS","LG","지주/기타"),
    ("034730.KS","SK","지주/기타"),
    ("097950.KS","CJ제일제당","지주/기타"),
    ("004370.KS","농심","지주/기타"),
    ("271560.KS","오리온","지주/기타"),
    ("009830.KS","한화솔루션","지주/기타"),
    ("000060.KS","메리츠화재","지주/기타"),
    ("138040.KS","메리츠금융지주","지주/기타"),
]

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
    ("ON","ON Semi","반도체"),
    ("MCHP","Microchip Tech","반도체"),
    ("ADI","Analog Devices","반도체"),
    ("TXN","Texas Instruments","반도체"),
    ("INTC","Intel","반도체"),
    ("ARM","Arm Holdings","반도체"),
    ("SNDK","SanDisk","반도체"),
    ("ASML","ASML","반도체"),
    ("TSM","TSMC","반도체"),
    ("STX","Seagate","반도체"),
    # 빅테크
    ("AAPL","Apple","빅테크"),
    ("MSFT","Microsoft","빅테크"),
    ("GOOGL","Alphabet","빅테크"),
    ("AMZN","Amazon","빅테크"),
    ("META","Meta","빅테크"),
    ("SMCI","Super Micro","빅테크"),
    ("ORCL","Oracle","빅테크"),
    ("IBM","IBM","빅테크"),
    ("HPE","HPE","빅테크"),
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
    ("FTNT","Fortinet","AI/소프트웨어"),
    ("OKTA","Okta","AI/소프트웨어"),
    ("TEAM","Atlassian","AI/소프트웨어"),
    ("WDAY","Workday","AI/소프트웨어"),
    ("SNOW","Snowflake","AI/소프트웨어"),
    ("NOW","ServiceNow","AI/소프트웨어"),
    ("ANSS","ANSYS","AI/소프트웨어"),
    ("ZM","Zoom","AI/소프트웨어"),
    ("DOCU","DocuSign","AI/소프트웨어"),
    ("S","SentinelOne","AI/소프트웨어"),
    ("HUBS","HubSpot","AI/소프트웨어"),
    ("MDB","MongoDB","AI/소프트웨어"),
    ("DKNG","DraftKings","AI/소프트웨어"),
    # 전기차/에너지
    ("TSLA","Tesla","전기차/에너지"),
    ("ENPH","Enphase","전기차/에너지"),
    ("FSLR","First Solar","전기차/에너지"),
    ("PLUG","Plug Power","전기차/에너지"),
    ("CHPT","ChargePoint","전기차/에너지"),
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
    ("DXCM","DexCom","바이오/헬스"),
    ("GEHC","GE HealthCare","바이오/헬스"),
    ("HOLX","Hologic","바이오/헬스"),
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
    ("EXPE","Expedia","소비재/유통"),
    ("AMZN","Amazon","소비재/유통"),
    # 금융/핀테크
    ("COIN","Coinbase","금융/핀테크"),
    ("PYPL","PayPal","금융/핀테크"),
    ("ADP","ADP","금융/핀테크"),
    ("PAYX","Paychex","금융/핀테크"),
    ("VRSK","Verisk","금융/핀테크"),
    ("HOOD","Robinhood","금융/핀테크"),
    # 미디어/통신
    ("NFLX","Netflix","미디어/통신"),
    ("CSCO","Cisco","미디어/통신"),
    ("FAST","Fastenal","미디어/통신"),
    ("PCAR","PACCAR","미디어/통신"),
    ("ODFL","Old Dominion","미디어/통신"),
    ("TMUS","T-Mobile","미디어/통신"),
    ("CMCSA","Comcast","미디어/통신"),
    ("WBD","Warner Bros Discovery","미디어/통신"),
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
    end   = datetime.today() + timedelta(days=1)
    start = end - timedelta(days=15)
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

            vol_today = float(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            vol_avg5  = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 and "Volume" in df.columns else vol_today
            vol_surge = round(vol_today / vol_avg5, 1) if vol_avg5 > 0 else 1.0

            streak = 0
            closes = df["Close"].tolist()
            if len(closes) >= 2:
                direction = 1 if closes[-1] > closes[-2] else -1
                for i in range(len(closes)-1, 0, -1):
                    if (closes[i] > closes[i-1]) == (direction == 1):
                        streak += direction
                    else:
                        break

            hist5 = []
            for i in range(min(5, len(df)-1), 0, -1):
                c = float(df["Close"].iloc[-i])
                p = float(df["Close"].iloc[-i-1])
                hist5.append(round((c-p)/p*100, 2))

            # ── 모멘텀 스코어 (최대 +50 / 최소 -30 범위) ──
            chg_score    = min(abs(chg_pct) * 2, 20) * (1 if chg_pct >= 0 else -1)
            vol_score    = min(vol_surge, 5) * 4
            streak_score = min(abs(streak), 5) * 2 * (1 if streak >= 0 else -1)
            momentum     = round(chg_score + vol_score + streak_score, 1)

            rows.append({
                "name"     : name,
                "ticker"   : ticker,
                "sector"   : sector,
                "close"    : round(close, 2),
                "chg_pct"  : chg_pct,
                "vol_surge": vol_surge,
                "streak"   : streak,
                "hist5"    : hist5,
                "momentum" : momentum,
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

# ── 코스피/나스닥 지수 수집 (마지막 거래일 종가 기준) ──────────────
kospi_index = nasdaq_index = kospi_chg = nasdaq_chg = None
try:
    end_dt = TARGET_DATE_OBJ + timedelta(days=1)
    start_dt = TARGET_DATE_OBJ - timedelta(days=7)
    for sym, key in [("^KS11","kospi"),("^IXIC","nasdaq")]:
        df = yf.download(sym, start=start_dt, end=end_dt, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(subset=["Close"])
        if len(df) >= 2:
            c = round(float(df["Close"].iloc[-1]), 2)
            p = round(float(df["Close"].iloc[-2]), 2)
            chg = round((c - p) / p * 100, 2)
            if key == "kospi": kospi_index, kospi_chg = c, chg
            else: nasdaq_index, nasdaq_chg = c, chg
    print(f"코스피: {kospi_index} ({kospi_chg}%), 나스닥: {nasdaq_index} ({nasdaq_chg}%)")
except Exception as e:
    print(f"지수 수집 실패: {e}")

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

import glob
cutoff = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
for old_file in glob.glob("history/*.json"):
    fname = os.path.basename(old_file).replace(".json","")
    if fname < cutoff:
        os.remove(old_file)
        print(f"오래된 파일 삭제: {old_file}")

print(f"✅ 완료! market_data.json + history/{TARGET_DATE}.json 저장됨")

# ── 텔레그램 브리핑 발송 ─────────────────────────────────────
import urllib.request as _req

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }).encode()
    try:
        req = _req.Request(url, data=payload,
                           headers={"Content-Type": "application/json"})
        with _req.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            if resp.get("ok"):
                print("✅ 텔레그램 발송 성공")
            else:
                print(f"텔레그램 오류: {resp}")
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def build_message(data, market):
    market_name = "코스피 🇰🇷" if market == "kospi" else "나스닥 🇺🇸"
    idx   = data.get("kospi_index" if market=="kospi" else "nasdaq_index")
    chg   = data.get("kospi_chg"   if market=="kospi" else "nasdaq_chg")
    up    = data.get(f"{market}_up",   [])[:5]
    down  = data.get(f"{market}_down", [])[:5]
    fng   = data.get("fng")
    fng_l = data.get("fng_label", "")

    arrow = "📈" if (chg or 0) >= 0 else "📉"
    chg_str = f"{chg:+.2f}%" if chg is not None else "—"
    idx_str = f"{idx:,.2f}" if idx else "—"

    # FNG
    fng_str = ""
    if fng is not None:
        emoji = "😱" if fng < 25 else "😰" if fng < 45 else "😐" if fng < 55 else "😊" if fng < 75 else "🤑"
        fng_str = f"\n{emoji} <b>공포탐욕지수</b>: {fng} ({fng_l})"

    # 상위 상승
    up_lines = "\n".join(
        [f"  {i+1}. {s.get('name', s.get('ticker',''))} <b>{s['chg_pct']:+.2f}%</b>"
         for i, s in enumerate(up)]
    )
    # 상위 하락
    dn_lines = "\n".join(
        [f"  {i+1}. {s.get('name', s.get('ticker',''))} <b>{s['chg_pct']:+.2f}%</b>"
         for i, s in enumerate(down)]
    )

    # 주도 섹터 top 3
    sectors = data.get(f"{market}_sectors", [])
    sec_lines = "\n".join(
        [f"  • {s['sector']} {s['avg_chg']:+.2f}%" for s in sectors[:3]]
    )

    msg = (
        f"📊 <b>데일리 마켓 브리핑</b> — {data.get('date','')}\n"
        f"{'─' * 28}\n"
        f"{arrow} <b>{market_name}</b>  {idx_str}  {chg_str}"
        f"{fng_str}\n\n"
        f"🟢 <b>상위 상승</b>\n{up_lines}\n\n"
        f"🔴 <b>상위 하락</b>\n{dn_lines}\n\n"
        f"🏷 <b>주도 섹터</b>\n{sec_lines}\n\n"
        f"🔗 <a href='https://market-reading.onrender.com'>대시보드 바로가기</a>"
    )
    return msg

TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if TG_TOKEN and TG_CHAT_ID:
    # 코스피 메시지
    kospi_msg  = build_message(result, "kospi")
    send_telegram(TG_TOKEN, TG_CHAT_ID, kospi_msg)
    # 나스닥 메시지
    nasdaq_msg = build_message(result, "nasdaq")
    send_telegram(TG_TOKEN, TG_CHAT_ID, nasdaq_msg)
else:
    print("텔레그램 환경변수 없음 — 발송 스킵 (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 설정 필요)")
