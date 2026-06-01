from flask import Flask, jsonify, render_template_string, request, Response
import json, os, urllib.request, glob
from datetime import datetime

app = Flask(__name__)
DATA_DIR  = "history"
DATA_FILE = "market_data.json"
os.makedirs(DATA_DIR, exist_ok=True)

GITHUB_USER   = "kwonbeen97"
GITHUB_REPO   = "market_reading"
GITHUB_BRANCH = "main"

def fetch_from_github(filename):
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{filename}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"GitHub fetch 실패 ({filename}): {e}")
        return None

STOCK_DESC = {
    "삼성전자":"한국 최대 반도체·스마트폰 기업. 메모리 반도체 세계 1위.",
    "SK하이닉스":"메모리 반도체(DRAM·NAND) 전문 기업. AI 수혜 HBM 핵심 공급사.",
    "삼성전기":"삼성 계열 전자부품 기업. MLCC·카메라모듈 세계 상위권.",
    "리노공업":"반도체 테스트 소켓 제조. 고마진 반도체 부품 강소 기업.",
    "한미반도체":"반도체 후공정 장비 기업. HBM 본딩 장비 핵심 공급사.",
    "한화에어로스페이스":"방산·항공엔진 전문 기업. K-방산 수출 대표주.",
    "두산에너빌리티":"원자력·가스터빈 발전설비 기업. SMR 테마 핵심주.",
    "한국전력":"국내 전력 독점 공급 공기업. 전기요금 정책 영향 큼.",
    "포스코인터내셔널":"POSCO 그룹 종합상사. 천연가스·이차전지소재 사업 확대.",
    "현대일렉트릭":"변압기·전력기기 제조. 북미 전력망 투자 수혜주.",
    "LS ELECTRIC":"배전·자동화 전력기기 국내 1위. 스마트그리드·ESS 사업 확대.",
    "효성중공업":"초고압 변압기·차단기 제조. 미국·유럽 전력망 투자 수혜주.",
    "LG에너지솔루션":"전기차 배터리 세계 2위. GM·현대차 등 글로벌 완성차 공급.",
    "삼성SDI":"삼성 계열 배터리 기업. 전기차·ESS 배터리 글로벌 공급.",
    "LG화학":"석유화학·배터리소재 대기업. NCC·양극재 사업 병행.",
    "에코프로비엠":"양극재 국내 1위. 전기차 배터리 핵심 소재 공급사.",
    "에코프로":"에코프로비엠 모회사. 양극재 테마 대표 지주사.",
    "삼성바이오로직스":"바이오의약품 CMO 세계 1위. 글로벌 제약사 위탁생산.",
    "셀트리온":"바이오시밀러 선도 기업. 유럽·미국 시장 진출 활발.",
    "유한양행":"국내 대표 제약사. 글로벌 기술이전 성과 다수.",
    "한미약품":"신약 개발 역량 강한 제약사. 기술수출 실적 우수.",
    "씨젠":"분자진단 전문 기업. 코로나 이후 글로벌 진단키트 공급.",
    "현대차":"국내 1위 완성차. 전기차·수소차 전환 중.",
    "기아":"현대차그룹 계열 완성차. EV6 등 전기차 글로벌 호평.",
    "현대모비스":"현대차그룹 핵심 부품사. 전동화 부품 전환 중.",
    "현대위아":"현대차그룹 파워트레인 부품사.",
    "한온시스템":"자동차 열관리 시스템 전문. 전기차 냉각 수요 수혜.",
    "NAVER":"국내 최대 포털·IT 플랫폼. 네이버페이·웹툰 등 사업 다각화.",
    "카카오":"카카오톡 기반 플랫폼 기업. 게임·금융·콘텐츠 계열사 다수.",
    "크래프톤":"배틀그라운드 개발사. 인도 등 신흥시장 게임 강자.",
    "삼성SDS":"삼성 IT서비스·물류 계열사. 클라우드·AI 전환 중.",
    "LG전자":"가전·TV 세계 상위권. 전장부품(VS사업부) 성장 중.",
    "KB금융":"KB국민은행 모회사. 국내 최대 금융그룹.",
    "신한지주":"신한은행 모회사. 아시아 진출 적극적인 금융그룹.",
    "하나금융":"KEB하나은행 모회사. 외환 부문 강점.",
    "우리금융":"우리은행 모회사. 기업금융 강점의 금융지주.",
    "삼성생명":"국내 1위 생명보험사. 삼성전자 지분 보유.",
    "현대중공업":"조선 세계 1위 그룹 계열. LNG선·컨테이너선 강자.",
    "한화오션":"대우조선해양 인수한 한화 조선사. LNG·군함 건조.",
    "삼성중공업":"드릴십·LNG선 전문 조선사. 해양플랜트 역량 보유.",
    "삼성물산":"삼성 그룹 지주·건설·상사. 삼성전자 주요 주주.",
    "HMM":"국내 최대 컨테이너 해운사. 운임 변동 민감.",
    "하이브":"BTS 소속사. K팝 글로벌 확장 선도 엔터사.",
    "에스엠":"아이돌 기획사 원조. 동방신기·엑소·에스파 등.",
    "JYP엔터":"트와이스·스트레이키즈 소속사. 일본·미국 시장 강세.",
    "와이지엔터":"블랙핑크·빅뱅 소속사. 글로벌 팬덤 보유.",
    "POSCO홀딩스":"철강 세계 4위. 이차전지 소재(리튬·양극재) 사업 확대.",
    "S-Oil":"사우디 아람코 계열 정유사. 석유화학 고도화 투자 중.",
    "LG":"LG그룹 지주사. LG전자·LG화학 등 주요 계열사 지분 보유.",
    "SK텔레콤":"국내 1위 이동통신사. AI·데이터센터 사업 확대.",
    "KT":"국내 2위 통신사. 기업 IT서비스·미디어 사업 병행.",
    "NVIDIA":"AI GPU 시장 독점적 1위. 데이터센터·자율주행 핵심 칩 공급.",
    "AMD":"CPU·GPU 2위 기업. AI 가속기 MI300X로 NVIDIA 추격 중.",
    "Broadcom":"네트워크 반도체·AI 가속기 설계. 애플 등 빅테크 핵심 공급사.",
    "Qualcomm":"모바일 AP·통신 모뎀 세계 1위. 온디바이스 AI 수혜.",
    "Applied Materials":"반도체 증착·식각 장비 1위. 파운드리 투자 최대 수혜.",
    "Lam Research":"반도체 식각 장비 전문. NAND·DRAM 투자 사이클 직결.",
    "KLA Corp":"반도체 계측·검사 장비 1위. 공정 미세화 필수 장비.",
    "Micron":"메모리 반도체(DRAM·NAND) 미국 유일 생산사. HBM 공급 확대.",
    "Marvell":"데이터센터 네트워킹 반도체. AI 클러스터 연결 칩 공급.",
    "NXP Semi":"차량용 반도체 세계 1위. 전기차·자율주행 수혜.",
    "Western Digital":"HDD·SSD 제조사.",
    "SanDisk":"낸드플래시·SSD 세계 2위. SanDisk 브랜드로 소비자 스토리지 시장 선도.",
    "Apple":"스마트폰·PC·웨어러블 세계 1위. 서비스 매출 고성장.",
    "Microsoft":"클라우드(Azure) 2위. OpenAI 투자로 AI 선도.",
    "Alphabet":"구글 모회사. 검색 광고·클라우드·유튜브 보유.",
    "Amazon":"이커머스·클라우드(AWS) 1위. AI 인프라 대규모 투자.",
    "Meta":"페이스북·인스타그램·왓츠앱 운영. AI·AR 글래스 투자.",
    "Super Micro":"AI 서버 조립·공급 전문. NVIDIA GPU 서버 최대 공급사.",
    "Palantir":"AI 데이터 분석 플랫폼. 미 정부·군 계약 강점.",
    "CrowdStrike":"클라우드 기반 사이버보안 1위. AI 위협 탐지 선도.",
    "Palo Alto":"네트워크 보안 대기업. 제로트러스트·SASE 플랫폼.",
    "Datadog":"클라우드 모니터링·관측 플랫폼. 개발자 필수 툴.",
    "Zscaler":"클라우드 보안 접근 전문. 재택근무 확산 수혜.",
    "Cloudflare":"CDN·네트워크 보안 플랫폼. AI 추론 엣지 서비스 확대.",
    "Adobe":"크리에이티브 소프트웨어 독점. AI 생성 기능 Firefly 추가.",
    "Intuit":"TurboTax·QuickBooks 세금·회계 소프트웨어 1위.",
    "Cadence":"반도체 설계 자동화(EDA) 툴 1위. AI 칩 설계 필수.",
    "Synopsys":"반도체 EDA·IP 기업. Ansys 인수로 시뮬레이션 확장.",
    "Tesla":"전기차·에너지저장·자율주행 선도. 로보택시 기대감.",
    "Enphase":"태양광 마이크로인버터 1위. 분산 에너지 저장 시스템.",
    "First Solar":"박막 태양광 패널 미국 1위. IRA 수혜 국내 생산.",
    "Amgen":"바이오의약품 선도 기업. 비만치료제 파이프라인 보유.",
    "Gilead":"항바이러스·항암제 전문. HIV 치료제 시장 독점.",
    "Vertex":"낭포성섬유증 치료제 독점. 신장질환·통증 파이프라인.",
    "Regeneron":"안과·항암·아토피 치료제 강자. Dupixent 블록버스터.",
    "Intuitive Surgical":"로봇 수술 시스템 다빈치 독점. 수술 자동화 선도.",
    "Moderna":"mRNA 백신 플랫폼. 암·독감 mRNA 치료제 개발 중.",
    "IDEXX Labs":"반려동물 진단기기·소프트웨어 1위. 펫 산업 성장 수혜.",
    "Costco":"창고형 회원제 유통 1위. 불황에도 강한 구독 모델.",
    "Starbucks":"글로벌 커피 체인 1위. 중국 시장 회복이 주가 변수.",
    "O'Reilly Auto":"자동차 부품 유통 1위. 고령 차량 증가 수혜.",
    "Monster Beverage":"에너지 음료 북미 1위. 코카콜라 유통망 활용.",
    "MercadoLibre":"중남미 이커머스·핀테크 1위. 아마존·페이팔의 남미판.",
    "Coinbase":"미국 최대 암호화폐 거래소. 비트코인 ETF 수탁 서비스.",
    "Arm Holdings":"스마트폰 AP 설계 아키텍처 독점. AI 엣지 칩 확산 수혜.",
    "Netflix":"글로벌 OTT 1위. 광고 요금제·게임 서비스 확대.",
    "Cisco":"네트워크 장비·소프트웨어 1위. AI 데이터센터 네트워킹 수혜.",
    "ADP":"급여·인사관리 소프트웨어 1위. 고용 시장 지표와 연동.",
    "Paychex":"중소기업 급여·HR 서비스. 금리 수혜형 안정 성장주.",
}

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>데일리 마켓 브리핑</title>
<meta name="description" content="코스피·나스닥 주도 종목 실시간 분석">
<meta name="theme-color" content="#0f1117">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="마켓 브리핑">
<link rel="manifest" href="/manifest.json">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f1117;color:#e8eaed;min-height:100vh;transition:background .3s,color .3s}
body.light{background:#f5f5f7;color:#1d1d1f}
body.light .header{border-color:#e5e5ea}
body.light .tab{color:#999;border-color:#e5e5ea}
body.light .tab.active{color:#1d1d1f;border-color:#2563eb}
body.light .ind-card{background:#fff;border-color:#e5e5ea}
body.light .ind-label{color:#999}
body.light .ai-summary{background:#fff;border-color:#e5e5ea}
body.light .ai-summary-text{color:#444}
body.light #searchInput{background:#fff;border-color:#e5e5ea;color:#1d1d1f}
body.light #searchResults{background:#fff;border-color:#e5e5ea}
body.light .search-item:hover{background:#f5f5f7}
body.light .date-chip{background:#fff;border-color:#e5e5ea;color:#999}
body.light .date-chip.active{background:#2563eb;color:#fff}
body.light .view-tab{background:#fff;border-color:#e5e5ea;color:#999}
body.light .view-tab.active{background:#2563eb;color:#fff}
body.light .card{background:#fff;border-color:#e5e5ea}
body.light .stock-row{border-color:#f0f0f5}
body.light .stock-row:hover{background:#f5f5f7}
body.light .sname{color:#1d1d1f}
body.light .bar-bg{background:#e5e5ea}
body.light .price{color:#999}
body.light .section-label{color:#999}
body.light .sector-block{background:#fff;border-color:#e5e5ea}
body.light .sector-header{border-color:#f0f0f5}
body.light .sector-name{color:#1d1d1f}
body.light .h-flat{background:#e5e5ea;color:#666}
body.light .popup{background:#fff;border-color:#e5e5ea}
body.light .popup-handle{background:#e5e5ea}
body.light .popup-name{color:#1d1d1f}
body.light .popup-price-row{border-color:#f0f0f5}
body.light .popup-price-label{color:#999}
body.light .popup-price-val{color:#1d1d1f}
body.light .popup-desc{color:#666;border-color:#f0f0f5}
body.light .hist-label{color:#999}
body.light .updated{color:#aaa}
body.light .rank{color:#bbb}
body.light .momentum-bar-bg{background:#e5e5ea}
body.light .momentum-label{color:#999}
body.light .ai-brief-result{background:#f8f9fa;border-color:#e5e5ea;color:#444}
body.light .ai-brief-btn{background:#eff6ff;border-color:#2563eb;color:#2563eb}
body.light .sector-trend-box{background:#fff;border-color:#e5e5ea}
.theme-btn{background:none;border:1px solid #2a2d3a;border-radius:8px;padding:6px 10px;font-size:16px;cursor:pointer;line-height:1;transition:all .2s}
body.light .theme-btn{border-color:#e5e5ea}
.cal-btn{padding:5px 12px;font-size:12px;font-weight:600;border-radius:20px;cursor:pointer;border:1px solid #2a2d3a;background:#1a1d27;color:#888;transition:all .2s;margin:10px 16px 0;display:inline-block}
.cal-btn:hover{border-color:#2563eb;color:#2563eb}
body.light .cal-btn{background:#fff;border-color:#e5e5ea}
.cal-panel{display:none;margin:8px 16px 0;background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;overflow:hidden}
.cal-panel.show{display:block}
body.light .cal-panel{background:#fff;border-color:#e5e5ea}
.cal-header{padding:10px 14px;font-size:12px;font-weight:700;color:#888;letter-spacing:.5px;border-bottom:1px solid #1e2235}
body.light .cal-header{border-color:#f0f0f5;color:#aaa}
.cal-item{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid #1e2235;gap:10px}
.cal-item:last-child{border-bottom:none}
body.light .cal-item{border-color:#f0f0f5}
.cal-item:hover{background:#222535}
body.light .cal-item:hover{background:#f5f5f7}
.cal-date{font-size:11px;color:#555;min-width:48px;font-weight:600}
.cal-name{flex:1;font-size:13px;font-weight:500}
body.light .cal-name{color:#1d1d1f}
.cal-imp{font-size:10px;font-weight:700;padding:1px 6px;border-radius:4px}
.cal-imp.high{background:#7f1d1d;color:#fca5a5}
.cal-imp.mid{background:#1e3a5f;color:#93c5fd}
.cal-imp.low{background:#1a2a1a;color:#86efac}
.cal-days{font-size:11px;color:#555;min-width:40px;text-align:right}
.cal-today{background:#1e2a1e}
body.light .cal-today{background:#f0fff0}
.header{padding:16px 16px 0;padding-top:max(16px,env(safe-area-inset-top));border-bottom:1px solid #1e2235}
.header-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.header h1{font-size:18px;font-weight:700}
.refresh-btn{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:7px 14px;font-size:13px;cursor:pointer;font-weight:600}
.tabs{display:flex}
.tab{flex:1;padding:11px 8px;text-align:center;font-size:13px;font-weight:600;cursor:pointer;color:#666;border-bottom:2px solid transparent;transition:all .2s}
.tab.active{color:#e8eaed;border-bottom-color:#2563eb}
.indicators{display:flex;gap:6px;padding:10px 16px;overflow-x:auto;scrollbar-width:none}
.indicators::-webkit-scrollbar{display:none}
.ind-card{flex-shrink:0;background:#1a1d27;border:1px solid #2a2d3a;border-radius:10px;padding:8px 12px;min-width:90px}
.ind-label{font-size:10px;color:#666;margin-bottom:3px;white-space:nowrap}
.ind-value{font-size:14px;font-weight:700;white-space:nowrap}
.ind-chg{font-size:11px;margin-top:2px}
.up{color:#22c55e}.down{color:#ef4444}.neutral{color:#888}
.ai-summary{margin:0 16px;background:#1a1d27;border-radius:12px;border:1px solid #2a2d3a;padding:12px 14px}
.ai-summary-label{font-size:10px;font-weight:700;color:#2563eb;letter-spacing:.8px;margin-bottom:6px}
.ai-summary-text{font-size:13px;color:#ccc;line-height:1.6}
.ai-loading{display:flex;align-items:center;gap:6px;color:#555;font-size:13px}
.ai-dot{width:5px;height:5px;border-radius:50%;background:#2563eb;animation:pulse 1.2s infinite}
.ai-dot:nth-child(2){animation-delay:.2s}.ai-dot:nth-child(3){animation-delay:.4s}
@keyframes pulse{0%,100%{opacity:.3}50%{opacity:1}}
.search-wrap{padding:10px 16px 0;position:relative}
#searchInput{width:100%;padding:10px 14px;border-radius:10px;border:1px solid #2a2d3a;background:#1a1d27;color:#e8eaed;font-size:14px;outline:none}
#searchInput::placeholder{color:#555}
#searchInput:focus{border-color:#2563eb}
#searchResults{display:none;position:absolute;left:16px;right:16px;top:52px;background:#1a1d27;border:1px solid #2a2d3a;border-radius:10px;z-index:50;overflow:hidden;max-height:280px;overflow-y:auto}
.search-item{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid #1e2235;cursor:pointer;transition:background .15s}
.search-item:hover{background:#222535}
.search-item:last-child{border-bottom:none}
.search-item-name{font-size:14px;font-weight:500;flex:1}
.search-item-sector{font-size:10px;padding:1px 7px;border-radius:4px;font-weight:600;margin-right:10px}
.search-item-chg{font-size:14px;font-weight:700;min-width:60px;text-align:right}
.date-bar{display:flex;gap:6px;padding:10px 16px 0;overflow-x:auto;scrollbar-width:none}
.date-bar::-webkit-scrollbar{display:none}
.date-chip{flex-shrink:0;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid #2a2d3a;background:#1a1d27;color:#888;transition:all .2s}
.date-chip.active{background:#2563eb;color:#fff;border-color:#2563eb}
.view-tabs{display:flex;gap:6px;padding:10px 16px 0}
.view-tab{padding:6px 14px;font-size:12px;font-weight:600;border-radius:20px;cursor:pointer;border:1px solid #2a2d3a;background:#1a1d27;color:#888;transition:all .2s}
.view-tab.active{background:#2563eb;color:#fff;border-color:#2563eb}
.content{padding:10px 16px 24px}
.section-label{font-size:11px;font-weight:700;letter-spacing:.8px;color:#555;margin:12px 0 6px;display:flex;align-items:center;gap:6px}
.dot{width:6px;height:6px;border-radius:50%}
.card{background:#1a1d27;border-radius:12px;border:1px solid #2a2d3a;overflow:hidden;margin-bottom:8px}
.stock-row{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid #1e2235;cursor:pointer;transition:background .15s}
.stock-row:hover{background:#222535}
.stock-row:last-child{border-bottom:none}
.rank{font-size:11px;color:#444;width:18px;flex-shrink:0}
.info{flex:0 0 120px;min-width:0}
.sname{font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sector-tag{display:inline-block;font-size:10px;padding:1px 6px;border-radius:4px;margin-top:2px;font-weight:600}
.bar-wrap{flex:1;margin:0 10px}
.bar-bg{height:3px;background:#2a2d3a;border-radius:2px}
.bar-fill{height:3px;border-radius:2px}
.price{font-size:12px;color:#666;margin-right:10px;white-space:nowrap}
.chg{font-size:14px;font-weight:700;min-width:64px;text-align:right;white-space:nowrap}
.heatmap{display:grid;gap:4px;margin-top:8px}
.sector-block{background:#1a1d27;border-radius:10px;border:1px solid #2a2d3a;overflow:hidden}
.sector-header{padding:8px 12px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.06)}
.sector-name{font-size:12px;font-weight:700;color:#fff}
.sector-avg{font-size:13px;font-weight:700}
.stocks-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:3px;padding:6px}
.heat-cell{border-radius:6px;padding:6px 8px;min-height:52px;display:flex;flex-direction:column;justify-content:space-between;cursor:pointer;transition:opacity .15s}
.heat-cell:hover{opacity:.8}
.heat-name{font-size:11px;font-weight:600;line-height:1.3;word-break:keep-all}
.heat-chg{font-size:13px;font-weight:700;margin-top:2px}
.h-up-3{background:#14532d;color:#86efac}.h-up-2{background:#166534;color:#bbf7d0}
.h-up-1{background:#15803d;color:#dcfce7}.h-flat{background:#1e2235;color:#888}
.h-dn-1{background:#7f1d1d;color:#fecaca}.h-dn-2{background:#991b1b;color:#fee2e2}.h-dn-3{background:#b91c1c;color:#fff}
.updated{text-align:center;font-size:11px;color:#444;padding:12px 0 4px}
/* 섹터 흐름 추이 */
.sector-trend-box{background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;padding:12px 14px;margin-bottom:12px}
.sector-trend-title{font-size:11px;font-weight:700;color:#555;letter-spacing:.5px;margin-bottom:8px}
.sector-trend-canvas{width:100%;height:160px;display:block;min-height:0}
/* 팝업 */
.popup-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);z-index:100;align-items:flex-end;justify-content:center}
.popup-overlay.show{display:flex}
.popup{background:#1a1d27;border-radius:16px 16px 0 0;border:1px solid #2a2d3a;padding:20px;width:100%;max-width:540px;animation:slideUp .25s ease;max-height:90vh;overflow-y:auto}
@keyframes slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.popup-handle{width:36px;height:4px;background:#2a2d3a;border-radius:2px;margin:0 auto 16px}
.popup-name{font-size:20px;font-weight:700;margin-bottom:4px}
.popup-sector{font-size:12px;margin-bottom:12px}
.popup-chg{font-size:28px;font-weight:700;margin-bottom:12px}
.popup-price-row{display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid #1e2235}
.popup-price-label{font-size:12px;color:#666}
.popup-price-val{font-size:14px;font-weight:500}
.popup-desc{font-size:13px;color:#aaa;line-height:1.7;padding:12px 0;border-top:1px solid #1e2235;margin-top:4px}
.hist-row{display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-top:1px solid #1e2235}
.hist-label{font-size:11px;color:#666}
.hist-val{font-size:12px;font-weight:600}
.popup-close{width:100%;padding:12px;background:#2563eb;border:none;border-radius:10px;color:#fff;font-size:15px;font-weight:600;cursor:pointer;margin-top:12px}
.popup-chart-wrap{margin:12px 0;border-top:1px solid #1e2235;padding-top:12px}
.popup-chart-label{font-size:11px;color:#555;font-weight:700;letter-spacing:.5px;margin-bottom:6px}
.popup-chart-canvas{width:100%;height:80px;display:block}
body.light .popup-chart-wrap{border-color:#f0f0f5}
/* 모멘텀 스코어 */
.momentum-wrap{margin:10px 0;padding:10px 0;border-top:1px solid #1e2235}
.momentum-label{font-size:11px;color:#666;display:flex;justify-content:space-between;margin-bottom:5px}
.momentum-bar-bg{height:6px;background:#2a2d3a;border-radius:3px;overflow:hidden}
.momentum-bar-fill{height:6px;border-radius:3px;transition:width .5s ease}
body.light .momentum-wrap{border-color:#f0f0f5}
body.light .momentum-bar-bg{background:#e5e5ea}
/* AI 종목 브리핑 */
.ai-brief-btn{width:100%;padding:10px;background:#1e2a3a;border:1px solid #2563eb;border-radius:10px;color:#60a5fa;font-size:13px;font-weight:600;cursor:pointer;transition:all .2s;margin-top:10px}
.ai-brief-btn:hover{background:#2563eb;color:#fff}
.ai-brief-btn:disabled{opacity:.5;cursor:not-allowed}
.ai-brief-result{margin-top:10px;padding:12px;background:#111827;border:1px solid #2a2d3a;border-radius:10px;font-size:13px;color:#ccc;line-height:1.7;display:none;white-space:pre-wrap}
body.light .ai-brief-btn{background:#eff6ff;border-color:#2563eb;color:#2563eb}
body.light .ai-brief-btn:hover{background:#2563eb;color:#fff}
body.light .ai-brief-result{background:#f8f9fa;border-color:#e5e5ea;color:#444}
/* 뱃지 */
.badge-streak-up{display:inline-block;font-size:10px;font-weight:700;background:#14532d;color:#86efac;padding:1px 5px;border-radius:4px;margin-left:4px}
.badge-streak-dn{display:inline-block;font-size:10px;font-weight:700;background:#7f1d1d;color:#fecaca;padding:1px 5px;border-radius:4px;margin-left:4px}
.badge-vol{display:inline-block;font-size:10px;font-weight:700;background:#1e3a5f;color:#60a5fa;padding:1px 5px;border-radius:4px;margin-left:4px}
.search-spark{display:inline-block;vertical-align:middle;margin-left:8px}
.share-btn{background:#1e2235;border:1px solid #2a2d3a;border-radius:8px;color:#888;font-size:13px;padding:6px 12px;cursor:pointer;transition:all .2s}
.share-btn:hover{border-color:#2563eb;color:#2563eb}
body.light .share-btn{background:#f5f5f7;border-color:#e5e5ea}
.fav-btn{background:none;border:none;font-size:18px;cursor:pointer;padding:0 4px;line-height:1;opacity:.5;transition:opacity .2s}
.fav-btn.active{opacity:1}
.fav-tab{display:flex;gap:6px;padding:0 16px;overflow-x:auto;scrollbar-width:none;flex-wrap:wrap;margin-top:4px}
.fav-chip{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:600;background:#1a1d27;border:1px solid #2a2d3a;cursor:pointer;transition:all .2s}
.fav-chip:hover{border-color:#2563eb}
.fav-chip .fav-chg{font-size:11px;font-weight:700}
.fav-empty{padding:10px 16px;font-size:12px;color:#555}
body.light .fav-chip{background:#fff;border-color:#e5e5ea}
</style>
</head>
<body>
<div class="header">
  <div class="header-top">
    <h1>📊 데일리 마켓 브리핑</h1>
    <div style="display:flex;gap:8px;align-items:center">
      <button class="theme-btn" id="themeBtn" onclick="toggleTheme()" title="라이트/다크 모드">🌙</button>
      <button class="refresh-btn" onclick="loadAll()">새로고침</button>
    </div>
  </div>
  <div class="tabs">
    <div class="tab active" onclick="switchMarket('kospi',this)">코스피</div>
    <div class="tab" onclick="switchMarket('nasdaq',this)">나스닥</div>
  </div>
</div>

<div class="indicators" id="indicators">
  <div class="ind-card"><div class="ind-label">코스피</div><div class="ind-value" id="kospi-idx">—</div><div class="ind-chg neutral" id="kospi-idx-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">나스닥</div><div class="ind-value" id="nasdaq-idx">—</div><div class="ind-chg neutral" id="nasdaq-idx-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">USD/KRW</div><div class="ind-value" id="usd">—</div><div class="ind-chg neutral" id="usd-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">미국 10년물</div><div class="ind-value" id="tnx">—</div><div class="ind-chg neutral" id="tnx-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">WTI 원유</div><div class="ind-value" id="oil">—</div><div class="ind-chg neutral" id="oil-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">금 (Gold)</div><div class="ind-value" id="gold">—</div><div class="ind-chg neutral" id="gold-c">로딩중</div></div>
  <div class="ind-card"><div class="ind-label">비트코인</div><div class="ind-value" id="btc">—</div><div class="ind-chg neutral" id="btc-c">로딩중</div></div>
</div>

<div class="ai-summary" style="margin-top:10px">
  <div class="ai-summary-label">✦ AI 시장 요약</div>
  <div class="ai-loading" id="aiLoading"><span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span><span style="margin-left:4px">분석 중...</span></div>
  <div class="ai-summary-text" id="aiText" style="display:none"></div>
</div>

<button class="cal-btn" onclick="toggleCal()">📅 경제지표 캘린더</button>
<div class="cal-panel" id="calPanel">
  <div class="cal-header">🇺🇸 미국 주요 경제지표 일정</div>
  <div id="calItems"></div>
</div>

<div class="search-wrap">
  <input type="text" id="searchInput" placeholder="🔍  종목 검색  (예: 삼성전자, NVDA)" oninput="onSearch(this.value)">
  <div id="searchResults"></div>
</div>

<div id="favBar"></div>
<div class="date-bar" id="dateBar"></div>

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
    <div class="sector-trend-box">
      <div class="sector-trend-title" id="sectorTrendTitle">📊 오늘 섹터별 등락률</div>
      <canvas class="sector-trend-canvas" id="sectorTrendCanvas" height="160"></canvas>
    </div>
    <div class="heatmap" id="heatmap-grid"></div>
  </div>
  <div class="updated" id="updatedAt"></div>
</div>

<!-- 팝업 -->
<div class="popup-overlay" id="popupOverlay" onclick="if(event.target===this)this.classList.remove('show')">
  <div class="popup">
    <div class="popup-handle"></div>
    <div style="display:flex;align-items:center;justify-content:space-between">
      <div class="popup-name" id="popupName"></div>
      <button class="fav-btn" id="favBtn" onclick="toggleFav()">☆</button>
    </div>
    <div class="popup-sector" id="popupSector"></div>
    <div class="popup-chg" id="popupChg"></div>
    <div class="popup-price-row">
      <div><div class="popup-price-label">현재가</div><div class="popup-price-val" id="popupPrice"></div></div>
      <div style="text-align:right"><div class="popup-price-label">티커</div><div class="popup-price-val" id="popupTicker"></div></div>
    </div>
    <div style="margin:8px 0" id="popupExtra"></div>
    <div class="popup-desc" id="popupDesc"></div>
    <!-- 모멘텀 스코어 -->
    <div class="momentum-wrap" id="popupMomentum"></div>
    <div id="popupHist"></div>
    <!-- AI 종목 브리핑 -->
    <button class="ai-brief-btn" id="aiBriefBtn" onclick="loadStockBrief()">✦ AI 종목 브리핑 생성</button>
    <div class="ai-brief-result" id="aiBriefResult"></div>
    <!-- 차트 -->
    <div class="popup-chart-wrap" id="popupChartWrap" style="display:none">
      <div class="popup-chart-label">📈 1개월 주가 흐름</div>
      <canvas class="popup-chart-canvas" id="popupChartCanvas" height="80"></canvas>
    </div>
    <div style="display:flex;gap:8px;margin-top:12px">
      <button class="share-btn" onclick="shareStock()" style="flex:0 0 auto">📤 공유</button>
      <button class="popup-close" onclick="document.getElementById('popupOverlay').classList.remove('show')" style="flex:1;margin-top:0">닫기</button>
    </div>
  </div>
</div>

<script>
let data=null,market='kospi',view='list',dates=[],currentDate='',allData={};
const DESC=__STOCK_DESC__;
const SECTOR_COLORS={
  '반도체':'#6366f1','반도체장비':'#818cf8',
  'AI/소프트웨어':'#8b5cf6','소프트웨어':'#8b5cf6',
  'IT플랫폼':'#3b82f6','IT서비스':'#60a5fa',
  '가전/전자':'#38bdf8','디스플레이':'#7dd3fc',
  '게임':'#a78bfa','게임/엔터':'#a78bfa',
  '사이버보안':'#06b6d4','네트워크':'#0891b2','AI인프라':'#7c3aed',
  '이차전지':'#22c55e','전기차/에너지':'#10b981',
  '신재생에너지':'#16a34a','에너지/발전':'#4ade80',
  '전력기기':'#86efac','정유':'#84cc16','에너지':'#65a30d',
  '바이오':'#ec4899','바이오/헬스':'#ec4899',
  '제약':'#f472b6','의료기기':'#fb7185',
  '자동차':'#14b8a6','자동차부품':'#2dd4bf','전기차':'#0d9488',
  '금융':'#818cf8','보험':'#a855f7','증권':'#9333ea',
  '금융/핀테크':'#c084fc','핀테크':'#c084fc',
  '소비재':'#f97316','소비재/유통':'#f97316',
  '유통':'#fb923c','음식료':'#fbbf24','이커머스':'#fcd34d',
  '방산':'#38bdf8','방산/항공':'#7dd3fc','방산/무역':'#bae6fd',
  '조선':'#0ea5e9','해운':'#0284c7','항공':'#60a5fa',
  '건설':'#f59e0b','건설/지주':'#d97706',
  '무역/자원':'#a3e635',
  '철강':'#f87171','비철금속':'#fca5a5',
  '화학':'#fb923c','소재/지주':'#fdba74',
  '엔터':'#f43f5e','미디어/통신':'#fb7185',
  '통신':'#34d399','미디어':'#6ee7b7',
  '빅테크':'#3b82f6','지주사':'#94a3b8',
  'IT기술':'#6366f1','기타':'#6b7280',
  '코스피':'#6366f1','나스닥':'#3b82f6',
  'IT/플랫폼':'#3b82f6','바이오/제약':'#ec4899',
  '자동차/부품':'#14b8a6','금융/보험':'#8b5cf6',
  '조선/해운/항공':'#0ea5e9','방산/전력':'#38bdf8',
  '소재/에너지':'#84cc16','소재/철강/화학':'#f97316',
  '게임/엔터':'#f43f5e','통신/건설/유통':'#34d399',
  '지주/기타':'#94a3b8',
};

function switchMarket(m,el){market=m;document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');render();loadAISummary();}
function switchView(v,el){
  view=v;
  document.querySelectorAll('.view-tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('list-view').style.display=v==='list'?'':'none';
  document.getElementById('heatmap-view').style.display=v==='heatmap'?'':'none';
  render();
  if(v==='heatmap') setTimeout(renderSectorTrend, 80);
}
function heatClass(v){if(v>5)return 'h-up-3';if(v>2)return 'h-up-2';if(v>0)return 'h-up-1';if(v>-2)return 'h-flat';if(v>-5)return 'h-dn-1';if(v>-8)return 'h-dn-2';return 'h-dn-3';}

// 검색
let _allStocks=[],_searchTimer=null;
function buildSearchIndex(){
  if(!data)return;
  const seen=new Set();_allStocks=[];
  const all=[...(data.kospi_up||[]),...(data.kospi_down||[]),...(data.nasdaq_up||[]),...(data.nasdaq_down||[])];
  all.forEach(s=>{const k=s.ticker||s.name;if(!seen.has(k)){seen.add(k);_allStocks.push(s);}});
  ['kospi_sectors','nasdaq_sectors'].forEach(k=>{(data[k]||[]).forEach(sec=>{(sec.stocks||[]).forEach(s=>{const k2=s.ticker||s.name;if(!seen.has(k2)){seen.add(k2);_allStocks.push(s);}});});});
}
function onSearch(q){
  const box=document.getElementById('searchResults');
  if(!q.trim()){box.style.display='none';return;}
  const kw=q.toLowerCase();
  const local=_allStocks.filter(s=>(s.name||s.ticker||'').toLowerCase().includes(kw)||(s.ticker||'').toLowerCase().includes(kw)).slice(0,8);
  renderSearchResults(local,box);
  clearTimeout(_searchTimer);
  _searchTimer=setTimeout(async()=>{
    try{
      box.innerHTML+='<div id="sload" style="padding:8px 14px;font-size:12px;color:#555">🔍 더 찾는 중...</div>';
      const res=await fetch('/api/search?q='+encodeURIComponent(q));
      const hits=await res.json();
      document.getElementById('sload')?.remove();
      if(hits.length>local.length)renderSearchResults(hits,box);
    }catch(e){}
  },500);
}
function renderSearchResults(hits,box){
  if(!hits.length){box.style.display='block';box.innerHTML='<div style="padding:12px 14px;color:#555;font-size:13px">검색 결과 없음</div>';return;}
  box.style.display='block';
  box.innerHTML=hits.map(s=>{
    const nm=s.name||s.ticker||'';const sec=s.sector||'';
    const col=SECTOR_COLORS[sec]||'#666';const isUp=s.chg_pct>=0;
    const live=s.live?'<span style="font-size:10px;color:#2563eb;margin-left:4px">실시간</span>':'';
    const sd=JSON.stringify(s).replace(/"/g,'&quot;');
    const sparkId='spark-'+Math.random().toString(36).slice(2,6);
    const hist=(s.hist5||[]);
    const sparkHtml=hist.length?'<canvas class="search-spark" id="'+sparkId+'" width="60" height="24"></canvas>':'';
    const el='<div class="search-item" onclick="selectSearch(this)" data-stock="'+sd+'"><div class="search-item-name">'+nm+live+'</div>'+sparkHtml+'<span class="search-item-sector" style="background:'+col+'22;color:'+col+'">'+sec+'</span><div class="search-item-chg '+(isUp?'up':'down')+'">'+(isUp?'+':'')+s.chg_pct+'%</div></div>';
    if(hist.length) setTimeout(()=>{ const c=document.getElementById(sparkId); drawSparkline(c,hist,isUp?'#22c55e':'#ef4444'); },50);
    return el;
  }).join('');
}
function selectSearch(el){document.getElementById('searchInput').value='';document.getElementById('searchResults').style.display='none';openPopup(el);}
document.addEventListener('click',e=>{if(!e.target.closest('#searchInput')&&!e.target.closest('#searchResults'))document.getElementById('searchResults').style.display='none';});

// 팝업
function openPopup(el){
  const s=JSON.parse(el.getAttribute('data-stock')||'{}');
  const nm=s.name||s.ticker||'';const sec=s.sector||'';
  const col=SECTOR_COLORS[sec]||'#888';const cl=s.close||0;const isUp=s.chg_pct>=0;
  document.getElementById('popupName').textContent=nm;
  document.getElementById('popupSector').innerHTML='<span style="background:'+col+'22;color:'+col+';padding:2px 8px;border-radius:4px;font-weight:600">'+sec+'</span>';
  document.getElementById('popupChg').textContent=(isUp?'+':'')+s.chg_pct+'%';
  document.getElementById('popupChg').className='popup-chg '+(isUp?'up':'down');
  document.getElementById('popupPrice').textContent=cl?Number(cl).toLocaleString()+' '+(market==='kospi'?'원':'USD'):'–';
  document.getElementById('popupTicker').textContent=s.ticker||'–';
  document.getElementById('popupDesc').textContent=DESC[nm]||'종목 설명 준비 중입니다.';

  // streak/vol 뱃지
  let extraHtml='';
  if(s.streak>=2) extraHtml+='<span class="badge-streak-up">🔥'+s.streak+'일 연속 상승</span> ';
  else if(s.streak<=-2) extraHtml+='<span class="badge-streak-dn">📉'+Math.abs(s.streak)+'일 연속 하락</span> ';
  if(s.vol_surge>=2) extraHtml+='<span class="badge-vol">⚡거래량 '+s.vol_surge+'배 급증</span>';
  document.getElementById('popupExtra').innerHTML=extraHtml;

  // 모멘텀 스코어
  const mom=s.momentum??null;
  const momEl=document.getElementById('popupMomentum');
  if(momEl&&mom!==null){
    const pct=Math.min(Math.max((mom+30)/60*100,0),100);
    const col2=mom>=15?'#22c55e':mom>=5?'#60a5fa':mom>=-5?'#888':mom>=-15?'#f97316':'#ef4444';
    const label=mom>=15?'강한 상승 모멘텀':mom>=5?'상승 모멘텀':mom>=-5?'중립':mom>=-15?'하락 모멘텀':'강한 하락 모멘텀';
    momEl.innerHTML='<div class="momentum-label"><span>모멘텀 스코어</span><span style="color:'+col2+';font-weight:700">'+(mom>0?'+':'')+mom+' <span style="font-weight:400;color:#666;font-size:11px">'+label+'</span></span></div><div class="momentum-bar-bg"><div class="momentum-bar-fill" style="width:'+pct+'%;background:'+col2+'"></div></div>';
  } else if(momEl){
    momEl.innerHTML='';
  }

  // 과거 등락률
  let histHtml='';
  [...dates].sort().reverse().forEach(d=>{
    if(d===currentDate)return;
    const hd=allData[d];if(!hd)return;
    const all=[...(hd[market+'_up']||[]),...(hd[market+'_down']||[])];
    const found=all.find(x=>(x.name||x.ticker)===nm);
    if(found){const isU=found.chg_pct>=0;histHtml+='<div class="hist-row"><span class="hist-label">'+d+'</span><span class="hist-val '+(isU?'up':'down')+'">'+(isU?'+':'')+found.chg_pct+'%</span></div>';}
  });
  document.getElementById('popupHist').innerHTML=histHtml?'<div style="margin-top:8px;font-size:11px;color:#555;font-weight:700;letter-spacing:.5px">과거 등락률</div>'+histHtml:'';

  // AI 브리핑 초기화
  const briefResult=document.getElementById('aiBriefResult');
  const briefBtn=document.getElementById('aiBriefBtn');
  if(briefResult){briefResult.style.display='none';briefResult.innerHTML='';}
  if(briefBtn){briefBtn.textContent='✦ AI 종목 브리핑 생성';briefBtn.disabled=false;}

  _currentStock=s;
  updateFavBtn(s.ticker||s.name);
  document.getElementById('popupOverlay').classList.add('show');
  if(s.ticker) loadStockChart(s.ticker, isUp);
}

// AI 종목 브리핑
async function loadStockBrief(){
  if(!_currentStock)return;
  const s=_currentStock;
  const btn=document.getElementById('aiBriefBtn');
  const result=document.getElementById('aiBriefResult');
  if(!btn||!result)return;
  btn.disabled=true;
  btn.textContent='분석 중...';
  result.style.display='block';
  result.innerHTML='<div class="ai-loading"><span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span><span style="margin-left:6px">Claude가 분석 중입니다...</span></div>';
  try{
    const params=new URLSearchParams({
      name:s.name||s.ticker||'',
      ticker:s.ticker||'',
      sector:s.sector||'',
      chg:s.chg_pct,
      market:market
    });
    const res=await fetch('/api/stock_brief?'+params);
    const d=await res.json();
    result.innerHTML=d.brief||'분석 결과 없음';
    btn.textContent='✦ 다시 생성';
    btn.disabled=false;
  }catch(e){
    result.innerHTML='분석 생성 실패. 다시 시도해주세요.';
    btn.textContent='✦ AI 종목 브리핑 생성';
    btn.disabled=false;
  }
}

// 섹터 흐름 추이 차트
function renderSectorTrend(){
  const cv=document.getElementById('sectorTrendCanvas');
  const titleEl=document.getElementById('sectorTrendTitle');
  if(!cv)return;

  // history 데이터 구성
  const sectorMap={};
  [...dates].sort().forEach(d=>{
    const hd=allData[d];if(!hd)return;
    (hd[market+'_sectors']||[]).forEach(sec=>{
      if(!sectorMap[sec.sector])sectorMap[sec.sector]=[];
      sectorMap[sec.sector].push({d,avg:sec.avg_chg});
    });
  });

  const latest=allData[currentDate];
  const latestSectors=latest?(latest[market+'_sectors']||[]):[];
  if(!latestSectors.length){cv.style.display='none';return;}

  // 라인차트 가능 여부: 3일 이상 + 최소 1개 섹터가 3개 이상 포인트
  const hasEnoughData=dates.length>=3&&Object.values(sectorMap).some(pts=>pts.length>=3);

  cv.style.display='block';
  const W=cv.parentElement.offsetWidth||340;
  const H=160;
  cv.width=W;cv.height=H;
  const ctx=cv.getContext('2d');
  ctx.clearRect(0,0,W,H);

  if(!hasEnoughData){
    // ── HTML 바차트 모드 (데이터 부족 시, canvas 대신 div로) ──
    if(titleEl)titleEl.textContent='📊 오늘 섹터별 등락률';
    cv.style.display='none';
    let htmlEl=document.getElementById('sectorBarChart');
    if(!htmlEl){
      htmlEl=document.createElement('div');
      htmlEl.id='sectorBarChart';
      cv.parentElement.appendChild(htmlEl);
    }
    htmlEl.style.cssText='width:100%;padding:4px 0';
    const sorted=[...latestSectors].sort((a,b)=>b.avg_chg-a.avg_chg);
    // 상위 4 + 하위 4 (중복 제거)
    const show=[...sorted.slice(0,4),...sorted.slice(-4)].filter((s,i,a)=>a.findIndex(x=>x.sector===s.sector)===i);
    const maxAbs=Math.max(...show.map(s=>Math.abs(s.avg_chg)),0.5);
    htmlEl.innerHTML=show.map(sec=>{
      const isUp=sec.avg_chg>=0;
      const col=SECTOR_COLORS[sec.sector]||(isUp?'#22c55e':'#ef4444');
      const pct=Math.round(Math.abs(sec.avg_chg)/maxAbs*45); // 최대 45%
      const chgStr=(isUp?'+':'')+sec.avg_chg+'%';
      return `<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px">
        <div style="flex:0 0 72px;font-size:11px;color:#aaa;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${sec.sector}</div>
        <div style="flex:1;display:flex;align-items:center;gap:4px">
          <div style="flex:1;height:14px;background:#1e2235;border-radius:2px;overflow:hidden;position:relative">
            <div style="position:absolute;${isUp?'left:0':'right:0'};top:0;height:100%;width:${pct}%;background:${col}44;border-radius:2px"></div>
            <div style="position:absolute;${isUp?'left:0':'right:0'};top:0;height:100%;width:3px;background:${col}"></div>
          </div>
          <div style="flex:0 0 52px;font-size:11px;font-weight:700;color:${col};text-align:left">${chgStr}</div>
        </div>
      </div>`;
    }).join('');
    return;
  }
  // 라인차트 모드면 HTML 바차트 숨기기
  const oldBar=document.getElementById('sectorBarChart');
  if(oldBar)oldBar.style.display='none';
  cv.style.display='block';

  // ── 라인차트 모드 (3일 이상) ──
  if(titleEl)titleEl.textContent='📈 7일 섹터 흐름 추이';
  // 상위 상승 2 + 하위 하락 2 + 절댓값 1 = 5개 (중복 제거)
  const sorted=[...latestSectors].sort((a,b)=>b.avg_chg-a.avg_chg);
  const topUp=sorted.slice(0,2).map(s=>s.sector);
  const topDn=sorted.slice(-2).map(s=>s.sector);
  const topAbs=sorted.sort((a,b)=>Math.abs(b.avg_chg)-Math.abs(a.avg_chg)).slice(0,1).map(s=>s.sector);
  const topSectors=[...new Set([...topUp,...topDn,...topAbs])].slice(0,5);

  const allVals=topSectors.flatMap(sec=>(sectorMap[sec]||[]).map(p=>p.avg));
  if(!allVals.length)return;
  const minV=Math.min(...allVals,-0.5),maxV=Math.max(...allVals,0.5);
  const range=maxV-minV||1;
  const pad={t:12,b:22,l:6,r:60};
  const toY=v=>pad.t+(1-(v-minV)/range)*(H-pad.t-pad.b);
  // 0선
  ctx.beginPath();ctx.strokeStyle='#2a2d3a';ctx.lineWidth=1;ctx.setLineDash([4,4]);
  ctx.moveTo(pad.l,toY(0));ctx.lineTo(W-pad.r,toY(0));ctx.stroke();ctx.setLineDash([]);
  topSectors.forEach((sec,i)=>{
    const points=(sectorMap[sec]||[]).filter(p=>p.avg!=null);
    if(points.length<2)return;
    const col=SECTOR_COLORS[sec]||['#22c55e','#3b82f6','#f97316','#a855f7','#ef4444'][i%5];
    ctx.beginPath();
    points.forEach((p,j)=>{
      const x=pad.l+(j/(points.length-1))*(W-pad.l-pad.r);
      const y=toY(p.avg);
      j===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    });
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.lineJoin='round';ctx.stroke();
    // 오른쪽 레이블 (겹침 방지: y 클램핑)
    const last=points[points.length-1];
    const ly=Math.max(pad.t+8,Math.min(H-pad.b-2,toY(last.avg)-(i*1)));
    ctx.fillStyle=col;ctx.font='9px -apple-system,sans-serif';ctx.textAlign='left';
    ctx.fillText(sec.slice(0,5),W-pad.r+4,ly+3);
  });
  // x축 날짜
  ctx.fillStyle='#555';ctx.font='9px sans-serif';ctx.textAlign='center';
  const refSec=topSectors.find(s=>(sectorMap[s]||[]).length>=2);
  if(refSec){
    const pts=sectorMap[refSec];
    pts.forEach((p,i)=>{
      if(i===0||i===pts.length-1||pts.length<=5||(i%(Math.ceil(pts.length/4))===0)){
        const x=pad.l+(i/(pts.length-1||1))*(W-pad.l-pad.r);
        ctx.fillText(p.d.slice(5),x,H-5);
      }
    });
  }
}

function renderList(){
  const up=data[market+'_up']||[],dn=data[market+'_down']||[];
  const max=Math.max(...[...up,...dn].map(s=>Math.abs(s.chg_pct)),1);
  function rows(arr,isUp){
    if(!arr.length)return '<div style="padding:14px;text-align:center;color:#444;font-size:13px">데이터 없음</div>';
    return arr.map((s,i)=>{
      const nm=s.name||s.ticker||'';const sec=s.sector||'';
      const col=SECTOR_COLORS[sec]||'#666';const pct=Math.abs(s.chg_pct)/max*100;
      const cl=s.close||0;const price=cl?Number(cl).toLocaleString():'';
      const sd=JSON.stringify(s).replace(/"/g,'&quot;');
      let badges='';
      if(s.streak>=3) badges+='<span class="badge-streak-up">🔥'+s.streak+'일</span>';
      else if(s.streak<=-3) badges+='<span class="badge-streak-dn">📉'+Math.abs(s.streak)+'일</span>';
      if(s.vol_surge>=2) badges+='<span class="badge-vol">⚡'+s.vol_surge+'x</span>';
      // 모멘텀 스코어 표시 (상위 3개만)
      const momBadge=(i<3&&s.momentum!=null)?'<span style="font-size:9px;color:#888;margin-left:4px">M:'+(s.momentum>0?'+':'')+s.momentum+'</span>':'';
      return '<div class="stock-row" onclick="openPopup(this)" data-stock="'+sd+'"><div class="rank">'+(i+1)+'</div><div class="info"><div class="sname">'+nm+' '+badges+momBadge+'</div><span class="sector-tag" style="background:'+col+'22;color:'+col+'">'+sec+'</span></div><div class="bar-wrap"><div class="bar-bg"><div class="bar-fill" style="width:'+pct+'%;background:'+(isUp?'#22c55e':'#ef4444')+'"></div></div></div><div class="price">'+price+'</div><div class="chg '+(isUp?'up':'down')+'">'+(isUp?'+':'')+s.chg_pct+'%</div></div>';
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
    const cells=sec.stocks.map(s=>{
      const nm=s.name||s.ticker||'';
      const sd=JSON.stringify(s).replace(/"/g,'&quot;');
      return '<div class="heat-cell '+heatClass(s.chg_pct)+'" onclick="openPopup(this)" data-stock="'+sd+'"><div class="heat-name">'+nm+'</div><div class="heat-chg">'+(s.chg_pct>0?'+':'')+s.chg_pct+'%</div></div>';
    }).join('');
    const scol=SECTOR_COLORS[sec.sector]||'#6b7280';
    return '<div class="sector-block" style="border-color:'+scol+'44">'
      +'<div class="sector-header" style="background:'+scol+'18;border-bottom-color:'+scol+'33">'
      +'<span class="sector-name" style="color:'+scol+'">'+sec.sector+'</span>'
      +'<span class="sector-avg '+avgCls+'">'+(sec.avg_chg>0?'+':'')+sec.avg_chg+'%</span>'
      +'</div>'
      +'<div class="stocks-grid">'+cells+'</div></div>';
  }).join('');
}

function drawStockChart(prices, color){
  const wrap=document.getElementById('popupChartWrap');
  const cv=document.getElementById('popupChartCanvas');
  if(!cv||!prices.length){if(wrap)wrap.style.display='none';return;}
  wrap.style.display='block';
  setTimeout(()=>{
    const W=cv.parentElement.offsetWidth||300;
    const H=80;
    cv.width=W;cv.height=H;
    const ctx=cv.getContext('2d');
    ctx.clearRect(0,0,W,H);
    const min=Math.min(...prices),max=Math.max(...prices);
    const range=max-min||1;
    const toY=v=>H-((v-min)/range)*(H-10)-5;
    const grad=ctx.createLinearGradient(0,0,0,H);
    grad.addColorStop(0,color+'44');grad.addColorStop(1,color+'00');
    ctx.beginPath();
    prices.forEach((v,i)=>{const x=(i/(prices.length-1))*W;const y=toY(v);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
    ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();
    ctx.fillStyle=grad;ctx.fill();
    ctx.beginPath();
    prices.forEach((v,i)=>{const x=(i/(prices.length-1))*W;const y=toY(v);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
    ctx.strokeStyle=color;ctx.lineWidth=2;ctx.lineJoin='round';ctx.stroke();
  },50);
}

async function loadStockChart(ticker,isUp){
  const wrap=document.getElementById('popupChartWrap');
  if(wrap)wrap.style.display='none';
  try{
    const res=await fetch('/api/chart?ticker='+encodeURIComponent(ticker));
    const d=await res.json();
    if(d.prices&&d.prices.length>1){drawStockChart(d.prices,isUp?'#22c55e':'#ef4444');}
  }catch(e){}
}

function render(){
  if(!data)return;
  document.getElementById('updatedAt').textContent='마지막 업데이트: '+(data.updated_at||'');
  buildSearchIndex();
  if(view==='list')renderList();else renderHeatmap();
}

function renderDateBar(){
  const bar=document.getElementById('dateBar');
  bar.innerHTML=dates.map(d=>'<div class="date-chip'+(d===currentDate?' active':'')+'" data-date="'+d+'" onclick="selectDate(this.dataset.date)">'+d.slice(5)+'</div>').join('');
}
function selectDate(d){currentDate=d;data=allData[d]||null;renderDateBar();render();loadAISummary();if(view==='heatmap')setTimeout(renderSectorTrend,80);}

async function loadIndicators(){
  try{
    const res=await fetch('/api/indicators');
    const d=await res.json();
    function set(id,val,chg){
      document.getElementById(id).textContent=val||'—';
      const el=document.getElementById(id+'-c');
      if(chg!=null){const isUp=chg>=0;el.textContent=(isUp?'+':'')+chg+'%';el.className='ind-chg '+(isUp?'up':'down');}
    }
    if(d.usd) set('usd',d.usd.toLocaleString()+'원',d.usd_chg);
    if(d.tnx){document.getElementById('tnx').textContent=d.tnx+'%';const el=document.getElementById('tnx-c');const isUp=d.tnx_chg>=0;el.textContent=(isUp?'+':'')+d.tnx_chg+'%p';el.className='ind-chg '+(isUp?'down':'up');}
    if(d.oil) set('oil','$'+d.oil,d.oil_chg);
    if(d.gold) set('gold','$'+d.gold.toLocaleString(),d.gold_chg);
    if(d.btc) set('btc','$'+Math.round(d.btc/1000)+'K',d.btc_chg);
    try{
      const md=await fetch('/api/data');const mdd=await md.json();
      function setIdx(id,val,chg){
        if(!val)return;const isUp=chg>=0;
        document.getElementById(id).textContent=val.toLocaleString();
        const el=document.getElementById(id+'-c');
        el.textContent=(isUp?'+':'')+chg+'%';el.className='ind-chg '+(isUp?'up':'down');
      }
      setIdx('kospi-idx',mdd.kospi_index,mdd.kospi_chg);
      setIdx('nasdaq-idx',mdd.nasdaq_index,mdd.nasdaq_chg);
    }catch(e2){}
  }catch(e){}
}

async function loadAISummary(){
  if(!data)return;
  document.getElementById('aiLoading').style.display='flex';
  document.getElementById('aiText').style.display='none';
  try{
    const res=await fetch('/api/summary?market='+market+'&date='+currentDate);
    const d=await res.json();
    document.getElementById('aiLoading').style.display='none';
    document.getElementById('aiText').style.display='block';
    document.getElementById('aiText').textContent=d.summary||'요약 불러오기 실패';
  }catch(e){
    document.getElementById('aiLoading').style.display='none';
    document.getElementById('aiText').style.display='block';
    document.getElementById('aiText').textContent='요약 불러오기 실패';
  }
}

// 경제지표 캘린더
const ECON_EVENTS=[
  {date:"2026-06-04",name:"ISM 서비스업 PMI",imp:"mid"},
  {date:"2026-06-05",name:"ADP 민간고용",imp:"high"},
  {date:"2026-06-06",name:"신규 실업수당 청구",imp:"mid"},
  {date:"2026-06-06",name:"무역수지",imp:"mid"},
  {date:"2026-06-10",name:"CPI (소비자물가지수)",imp:"high"},
  {date:"2026-06-11",name:"Core CPI",imp:"high"},
  {date:"2026-06-12",name:"PPI (생산자물가지수)",imp:"mid"},
  {date:"2026-06-17",name:"소매판매",imp:"high"},
  {date:"2026-06-17",name:"산업생산",imp:"mid"},
  {date:"2026-06-18",name:"FOMC 금리결정",imp:"high"},
  {date:"2026-06-18",name:"파월 의장 기자회견",imp:"high"},
  {date:"2026-06-25",name:"GDP (1분기 확정)",imp:"high"},
  {date:"2026-06-26",name:"PCE 물가지수",imp:"high"},
  {date:"2026-06-30",name:"시카고 PMI",imp:"mid"},
  {date:"2026-07-02",name:"비농업 고용 (NFP)",imp:"high"},
  {date:"2026-07-02",name:"실업률",imp:"high"},
  {date:"2026-07-08",name:"FOMC 의사록",imp:"mid"},
  {date:"2026-07-10",name:"CPI (소비자물가지수)",imp:"high"},
  {date:"2026-07-15",name:"소매판매",imp:"high"},
  {date:"2026-07-28",name:"FOMC 금리결정",imp:"high"},
  {date:"2026-07-28",name:"파월 의장 기자회견",imp:"high"},
  {date:"2026-07-30",name:"GDP (2분기 속보)",imp:"high"},
  {date:"2026-07-31",name:"PCE 물가지수",imp:"high"},
  {date:"2026-08-06",name:"비농업 고용 (NFP)",imp:"high"},
  {date:"2026-08-12",name:"CPI (소비자물가지수)",imp:"high"},
  {date:"2026-08-26",name:"잭슨홀 심포지엄",imp:"high"},
  {date:"2026-09-16",name:"FOMC 금리결정",imp:"high"},
  {date:"2026-09-25",name:"PCE 물가지수",imp:"high"},
];
const IMP_LABEL={high:"중요",mid:"보통",low:"낮음"};
function renderCalendar(){
  const now=new Date();const today=now.toISOString().slice(0,10);
  const upcoming=ECON_EVENTS.filter(e=>e.date>=today).slice(0,12);
  const el=document.getElementById('calItems');
  if(!upcoming.length){el.innerHTML='<div style="padding:14px;text-align:center;color:#555;font-size:13px">예정된 일정 없음</div>';return;}
  el.innerHTML=upcoming.map(e=>{
    const eDate=new Date(e.date+'T00:00:00');
    const diff=Math.round((eDate-now)/86400000);
    const isToday=e.date===today;
    const daysStr=isToday?'오늘':diff===1?'내일':diff+'일 후';
    const dStr=e.date.slice(5).replace('-','/');
    return '<div class="cal-item'+(isToday?' cal-today':'')+'"><div class="cal-date">'+dStr+'</div><div class="cal-name">'+e.name+'</div><span class="cal-imp '+e.imp+'">'+IMP_LABEL[e.imp]+'</span><div class="cal-days">'+daysStr+'</div></div>';
  }).join('');
}
function toggleCal(){const panel=document.getElementById('calPanel');panel.classList.toggle('show');if(panel.classList.contains('show'))renderCalendar();}

// 테마
function initTheme(){const saved=localStorage.getItem('theme')||'dark';if(saved==='light'){document.body.classList.add('light');document.getElementById('themeBtn').textContent='☀️';}}
function toggleTheme(){const isLight=document.body.classList.toggle('light');document.getElementById('themeBtn').textContent=isLight?'☀️':'🌙';localStorage.setItem('theme',isLight?'light':'dark');}
initTheme();

// 스파크라인
function drawSparkline(canvas,prices,color){
  if(!canvas||!prices||prices.length<2)return;
  const W=60,H=24;canvas.width=W;canvas.height=H;
  const ctx=canvas.getContext('2d');
  const min=Math.min(...prices),max=Math.max(...prices);
  const range=max-min||1;
  ctx.beginPath();
  prices.forEach((v,i)=>{const x=(i/(prices.length-1))*W;const y=H-((v-min)/range)*(H-4)-2;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
  ctx.strokeStyle=color;ctx.lineWidth=1.5;ctx.lineJoin='round';ctx.stroke();
}

// 종목 공유
async function shareStock(){
  if(!_currentStock)return;
  const s=_currentStock;
  const nm=s.name||s.ticker||'';const isUp=s.chg_pct>=0;
  const col=isUp?'#22c55e':'#ef4444';const chgStr=(isUp?'+':'')+s.chg_pct+'%';
  const price=s.close?Number(s.close).toLocaleString()+(market==='kospi'?' 원':' USD'):'';
  const sec=s.sector||'';const scol=SECTOR_COLORS[sec]||'#666';
  const desc=DESC[nm]||'';
  const cv=document.createElement('canvas');cv.width=680;cv.height=360;
  const ctx=cv.getContext('2d');
  ctx.fillStyle='#0f1117';ctx.roundRect(0,0,680,360,20);ctx.fill();
  ctx.fillStyle=scol+'33';ctx.roundRect(24,24,ctx.measureText(sec).width+24,28,6);ctx.fill();
  ctx.fillStyle=scol;ctx.font='bold 13px -apple-system,sans-serif';ctx.fillText(sec,36,42);
  ctx.fillStyle='#e8eaed';ctx.font='bold 36px -apple-system,sans-serif';ctx.fillText(nm,24,100);
  ctx.fillStyle=col;ctx.font='bold 52px -apple-system,sans-serif';ctx.fillText(chgStr,24,170);
  ctx.fillStyle='#888';ctx.font='16px -apple-system,sans-serif';ctx.fillText('현재가',24,210);
  ctx.fillStyle='#e8eaed';ctx.font='bold 20px -apple-system,sans-serif';ctx.fillText(price,24,235);
  if(desc){ctx.fillStyle='#666';ctx.font='14px -apple-system,sans-serif';const words=desc.split(' ');let line='',y=280;for(const w of words){const test=line+w+' ';if(ctx.measureText(test).width>620&&line){ctx.fillText(line,24,y);line=w+' ';y+=20;}else line=test;}ctx.fillText(line,24,y);}
  ctx.fillStyle='#333';ctx.font='12px -apple-system,sans-serif';ctx.textAlign='left';ctx.fillText('📊 데일리 마켓 브리핑',24,340);
  ctx.fillStyle='#444';ctx.textAlign='right';ctx.fillText(new Date().toLocaleDateString('ko-KR'),656,340);
  cv.toBlob(async blob=>{
    const file=new File([blob],'market-'+nm+'.png',{type:'image/png'});
    if(navigator.share&&navigator.canShare({files:[file]})){try{await navigator.share({files:[file],title:nm+' '+chgStr,text:nm+' '+chgStr+' | 데일리 마켓 브리핑'});}catch(e){}}
    else{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='market-'+nm+'.png';a.click();}
  },'image/png');
}

// 즐겨찾기
let _favs=JSON.parse(localStorage.getItem('favs')||'[]');
let _currentStock=null;
function toggleFav(){
  if(!_currentStock)return;
  const key=(_currentStock.ticker||_currentStock.name).replace(/[^a-zA-Z0-9가-힣.]/g,'_');
  const idx=_favs.findIndex(f=>f.key===key);
  if(idx>=0)_favs.splice(idx,1);
  else _favs.push({key,name:_currentStock.name||_currentStock.ticker,ticker:_currentStock.ticker,sector:_currentStock.sector});
  localStorage.setItem('favs',JSON.stringify(_favs));
  updateFavBtn(key);renderFavBar();
}
function updateFavBtn(key){
  const btn=document.getElementById('favBtn');if(!btn)return;
  const isFav=_favs.some(f=>f.key===key);
  btn.textContent=isFav?'★':'☆';btn.classList.toggle('active',isFav);
}
function renderFavBar(){
  const bar=document.getElementById('favBar');if(!bar)return;
  if(!_favs.length){bar.innerHTML='';return;}
  const allStocks=data?[...(data.kospi_up||[]),...(data.kospi_down||[]),...(data.nasdaq_up||[]),...(data.nasdaq_down||[]),...(data.kospi_sectors||[]).flatMap(s=>s.stocks||[]),...(data.nasdaq_sectors||[]).flatMap(s=>s.stocks||[])]:[];
  bar.innerHTML='<div class="fav-tab"></div>';
  const tab=bar.querySelector('.fav-tab');
  _favs.forEach(f=>{
    const found=allStocks.find(s=>((s.ticker||s.name).replace(/[^a-zA-Z0-9가-힣.]/g,'_'))===f.key);
    const chg=found?found.chg_pct:null;
    const col=chg!=null?(chg>=0?'#22c55e':'#ef4444'):'#888';
    const chgStr=chg!=null?(chg>=0?'+':'')+chg+'%':'';
    const chip=document.createElement('div');chip.className='fav-chip';
    if(found){const sd=JSON.stringify(found);chip.onclick=()=>{const el=document.createElement('div');el.setAttribute('data-stock',sd.replace(/"/g,'&quot;'));openPopup(el);};}
    chip.innerHTML='<span>'+f.name+'</span>'+(chgStr?'<span class="fav-chg" style="color:'+col+'">'+chgStr+'</span>':'');
    const x=document.createElement('span');x.textContent='×';x.style.cssText='color:#555;font-size:14px;padding:0 2px;cursor:pointer';
    x.onclick=e=>{e.stopPropagation();_favs=_favs.filter(f2=>f2.key!==f.key);localStorage.setItem('favs',JSON.stringify(_favs));renderFavBar();};
    chip.appendChild(x);tab.appendChild(chip);
  });
}

async function loadAll(){
  try{
    const r=await fetch('/api/history');const h=await r.json();
    dates=h.dates||[];allData=h.data||{};
    currentDate=dates[dates.length-1]||'';
    data=allData[currentDate]||null;
    renderDateBar();render();renderFavBar();loadAISummary();loadIndicators();
  }catch(e){}
}
loadAll();
</script>
</body>
</html>"""

@app.route("/")
def index():
    desc_json = json.dumps(STOCK_DESC, ensure_ascii=False)
    return render_template_string(HTML.replace("__STOCK_DESC__", desc_json))

@app.route("/api/history")
def api_history():
    all_data={};dates=[]
    latest=fetch_from_github("market_data.json")
    if latest:
        d=latest.get("date","")
        if d:all_data[d]=latest;dates.append(d)
    try:
        api_url=f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/history"
        gh_token=os.environ.get("GITHUB_TOKEN","")
        headers={"User-Agent":"Mozilla/5.0"}
        if gh_token:headers["Authorization"]=f"Bearer {gh_token}"
        req=urllib.request.Request(api_url,headers=headers)
        with urllib.request.urlopen(req,timeout=8) as r:
            files=json.loads(r.read())
        print(f"history 파일 목록: {[f['name'] for f in files]}")
        for f in sorted(files,key=lambda x:x["name"])[-7:]:
            fname=f["name"];date_key=fname.replace(".json","")
            if date_key in all_data:continue
            raw_url=f["download_url"]
            try:
                req2=urllib.request.Request(raw_url,headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req2,timeout=10) as r2:
                    d=json.loads(r2.read().decode("utf-8"))
                date=d.get("date","")
                if date and date not in all_data:all_data[date]=d;dates.append(date)
            except Exception as e2:
                print(f"  {fname} 로드 실패: {e2}")
    except Exception as e:
        print(f"history 목록 실패: {e}")
    dates=sorted(set(dates))
    return jsonify({"dates":dates,"data":all_data})

@app.route("/api/data")
def api_data():
    data=fetch_from_github("market_data.json")
    if data:return jsonify(data)
    return jsonify({"error":"데이터 없음"}),404

@app.route("/api/indicators")
def api_indicators():
    result={}
    try:
        import yfinance as yf
        symbols={"KRW=X":"usd","CL=F":"oil","GC=F":"gold","BTC-USD":"btc","^TNX":"tnx"}
        for sym,key in symbols.items():
            try:
                df=yf.download(sym,period="5d",auto_adjust=True,progress=False)
                if isinstance(df.columns,__import__('pandas').MultiIndex):df.columns=df.columns.get_level_values(0)
                closes=df["Close"].dropna().tolist()
                if len(closes)>=2:
                    v=closes[-1];chg=round((closes[-1]-closes[-2])/closes[-2]*100,2)
                    if key=="usd":result["usd"]=round(v);result["usd_chg"]=chg
                    elif key=="oil":result["oil"]=round(float(v),2);result["oil_chg"]=chg
                    elif key=="gold":result["gold"]=round(float(v));result["gold_chg"]=chg
                    elif key=="btc":result["btc"]=round(float(v));result["btc_chg"]=chg
                    elif key=="tnx":result["tnx"]=round(float(v),2);result["tnx_chg"]=round((closes[-1]-closes[-2])*100)/100
            except Exception as e2:
                print(f"{sym} 오류: {e2}")
    except Exception as e:
        error_msg = str(e)
        # Anthropic 서버가 보낸 구체적인 에러 메시지가 있다면 읽어옴
        if hasattr(e, 'read'):
            try:
                error_msg = e.read().decode('utf-8')
            except:
                pass
        
        # 비상용 텍스트 대신, 진짜 에러 원인을 웹페이지 요약창에 그대로 출력
        return jsonify({"summary": f"❌ API 에러 발생: {error_msg}"})

@app.route("/api/summary")
def api_summary():
    market=request.args.get("market","kospi")
    date=request.args.get("date","")
    data=None
    if date:data=fetch_from_github(f"history/{date}.json")
    if not data:data=fetch_from_github("market_data.json")
    if not data:return jsonify({"summary":"데이터 없음"})
    up=data.get(f"{market}_up",[])[:5];down=data.get(f"{market}_down",[])[:5]
    sectors=data.get(f"{market}_sectors",[])
    market_name="코스피" if market=="kospi" else "나스닥"
    up_str=", ".join([f"{s.get('name',s.get('ticker',''))}({s['chg_pct']:+.1f}%)" for s in up])
    down_str=", ".join([f"{s.get('name',s.get('ticker',''))}({s['chg_pct']:+.1f}%)" for s in down])
    sector_str=", ".join([f"{s['sector']}({s['avg_chg']:+.1f}%)" for s in sectors[:5]])
    prompt=f"""{data.get('date','')} {market_name} 시장 데일리 리딩입니다.

[시장 요약 데이터]
- 상위 상승 주도: {up_str}
- 상위 하락: {down_str}
- 주요 섹터 흐름: {sector_str}

전문적인 애널리스트의 시각으로 다음 조건에 맞춰 시황 브리핑을 작성해주세요:
1. 단순히 숫자를 나열하지 말고, 전체 지수 흐름과 주도 섹터(반도체, 빅테크 등) 간의 맥락을 짚어주세요.
2. 매크로 환경(국채 금리나 환율 변동 등)이 시장에 미칠 영향을 한 줄로 포함해주세요.
3. 통찰이 담긴 3~4문장의 자연스러운 한국어로 요약해주세요."""
    try:
        api_key=os.environ.get("ANTHROPIC_API_KEY","")
        if not api_key:
            return jsonify({"summary":f"{market_name} 상승 주도: {up_str} / 하락: {down_str}"})
        payload=json.dumps({"model":"claude-3-5-haiku-20241022","max_tokens":300,"messages":[{"role":"user","content":prompt}]}).encode()
        req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=payload,
            headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(req,timeout=15) as r:
            res=json.loads(r.read())
        return jsonify({"summary":res["content"][0]["text"]})
    except Exception as e:
        error_msg=str(e)
        if hasattr(e,'read'):error_msg=e.read().decode('utf-8')
        print(f"Claude API 호출 에러: {error_msg}")
        return jsonify({"summary":f"{market_name} 상승 주도: {up_str} / 하락: {down_str}"})

@app.route("/api/stock_brief")
def api_stock_brief():
    name   = request.args.get("name","")
    ticker = request.args.get("ticker","")
    sector = request.args.get("sector","")
    chg    = request.args.get("chg","0")
    market = request.args.get("market","kospi")
    market_name = "코스피" if market == "kospi" else "나스닥"

    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if not api_key:
        return jsonify({"brief":"API 키가 없어 분석을 생성할 수 없습니다."})

    prompt = f"""오늘 {name}({ticker}) 종목이 {chg}% 등락했습니다.
섹터: {sector} | 시장: {market_name}

아래 형식으로 한국어 종목 브리핑을 작성해주세요:
1. **오늘 흐름 해석** — 이 등락의 가능한 배경 (1~2문장)
2. **섹터 맥락** — {sector} 섹터 내 이 종목의 포지션과 투자자 관점 (1문장)
3. **주목 포인트** — 단기적으로 주의해야 할 리스크 또는 기회 요인 (1문장)

간결하고 전문적으로, 총 4~5문장 이내로 작성해주세요."""

    try:
        payload = json.dumps({
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 400,
            "messages": [{"role":"user","content":prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type":"application/json",
                "x-api-key":api_key,
                "anthropic-version":"2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read())
        return jsonify({"brief": res["content"][0]["text"]})
    except Exception as e:
        error_msg = str(e)
        if hasattr(e,'read'): error_msg = e.read().decode('utf-8')
        print(f"stock_brief 에러: {error_msg}")
        return jsonify({"brief":"분석 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."})

@app.route("/api/search")
def api_search():
    q=request.args.get("q","").strip()
    if not q:return jsonify([])
    import yfinance as yf
    from datetime import timedelta
    results=[]
    mdata=fetch_from_github("market_data.json")
    if mdata:
        all_stocks=[]
        for key in ["kospi_up","kospi_down","nasdaq_up","nasdaq_down"]:all_stocks.extend(mdata.get(key,[]))
        for sec in mdata.get("kospi_sectors",[])+mdata.get("nasdaq_sectors",[]):all_stocks.extend(sec.get("stocks",[]))
        seen=set();kw=q.lower()
        for s in all_stocks:
            nm=s.get("name","");tk=s.get("ticker","");key=tk or nm
            if key in seen:continue
            if kw in nm.lower() or kw in tk.lower():seen.add(key);results.append(s)
    if results:return jsonify(results[:10])
    KR_STOCKS={"삼성전자":"005930.KS","SK하이닉스":"000660.KS","삼성바이오로직스":"207940.KS","LG에너지솔루션":"373220.KS","삼성전기":"009150.KS","현대차":"005380.KS","기아":"000270.KS","POSCO홀딩스":"005490.KS","NAVER":"035420.KS","카카오":"035720.KS"}
    ticker=None
    for name2,tk in KR_STOCKS.items():
        if q in name2:ticker=tk;break
    if not ticker:ticker=q.upper()
    try:
        from datetime import datetime
        end=datetime.today();start=end-timedelta(days=10)
        df=yf.download(ticker,start=start,end=end,auto_adjust=True,progress=False)
        if isinstance(df.columns,__import__('pandas').MultiIndex):df.columns=df.columns.get_level_values(0)
        df=df.dropna(subset=["Close"])
        if len(df)>=2:
            close=float(df["Close"].iloc[-1]);prev=float(df["Close"].iloc[-2])
            chg=round((close-prev)/prev*100,2)
            name2=next((n for n,t in KR_STOCKS.items() if t==ticker),ticker)
            results.append({"name":name2,"ticker":ticker,"close":round(close,2),"chg_pct":chg,"sector":"코스피" if ticker.endswith(".KS") else "나스닥","live":True})
    except:pass
    return jsonify(results[:10])

@app.route("/api/chart")
def api_chart():
    ticker=request.args.get("ticker","")
    if not ticker:return jsonify({"prices":[]})
    try:
        import yfinance as yf
        from datetime import datetime,timedelta
        end=datetime.today()+timedelta(days=1);start=end-timedelta(days=35)
        df=yf.download(ticker,start=start,end=end,auto_adjust=True,progress=False)
        if isinstance(df.columns,__import__('pandas').MultiIndex):df.columns=df.columns.get_level_values(0)
        df=df.dropna(subset=["Close"])
        prices=[round(float(v),2) for v in df["Close"].tolist()]
        return jsonify({"prices":prices})
    except Exception as e:
        print(f"chart 오류: {e}")
        return jsonify({"prices":[]})

@app.route("/manifest.json")
def manifest():
    m={"name":"데일리 마켓 브리핑","short_name":"마켓 브리핑","description":"코스피·나스닥 주도 종목 실시간 분석","start_url":"/","display":"standalone","background_color":"#0f1117","theme_color":"#0f1117","orientation":"portrait","icons":[{"src":"/icon.svg","sizes":"192x192","type":"image/svg+xml"},{"src":"/icon.svg","sizes":"512x512","type":"image/svg+xml"}]}
    return Response(json.dumps(m),mimetype="application/json")

@app.route("/sw.js")
def service_worker():
    sw="""const CACHE='market-v1';self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/']))));self.addEventListener('fetch',e=>{if(e.request.url.includes('/api/'))return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));});"""
    return Response(sw,mimetype="application/javascript")

@app.route("/icon.svg")
def icon():
    svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect width="192" height="192" rx="40" fill="#0f1117"/><rect x="30" y="120" width="28" height="52" rx="4" fill="#22c55e"/><rect x="68" y="90" width="28" height="82" rx="4" fill="#22c55e"/><rect x="106" y="60" width="28" height="112" rx="4" fill="#2563eb"/><rect x="144" y="100" width="28" height="72" rx="4" fill="#ef4444"/><polyline points="44,115 82,85 120,55 158,95" stroke="#ffffff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
    return Response(svg,mimetype="image/svg+xml")

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
