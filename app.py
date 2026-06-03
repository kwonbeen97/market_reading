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
    "엔씨소프트":"리니지·블레이드&소울 개발사. 국내 대형 게임사 대표주.",
    "넷마블":"모바일 게임 대형사. 나이언틱·방탄소년단 게임 등 글로벌 진출.",
    "펄어비스":"검은사막 개발사. 붉은사막 출시 기대감 보유.",
    "솔브레인홀딩스":"반도체·디스플레이 소재 솔브레인 지주사.",
    "솔브레인":"반도체 식각액·세정액 전문. 삼성·SK하이닉스 핵심 소재 공급.",
    "원익IPS":"반도체 CVD·ALD 장비 전문. 삼성·SK 장비 공급사.",
    "파크시스템스":"원자력현미경(AFM) 세계 1위. 반도체 계측 장비 강자.",
    "브이원텍":"반도체·디스플레이 검사장비 전문 기업.",
    "고영":"3D 검사장비 세계 1위. 스마트팩토리·반도체 패키징 수요 수혜.",
    "효성첨단소재":"탄소섬유·아라미드 국내 1위. 수소탱크·방탄복 핵심 소재.",
    "에코앤드림":"이차전지 양극활물질 전구체 전문 기업.",
    "SNT모티브":"전기차 구동모터·방산부품 제조. 현대차그룹 공급사.",
    "오리엔트바이오":"동물용 의약품·실험동물 전문 기업.",
    "엑세스바이오":"체외진단 의료기기 전문. 말라리아·코로나 진단키트 글로벌 수출.",
    "계양전기":"전동공구·모터 제조사. 이차전지 팩 사업 진출.",
    "한국타이어":"한국타이어앤테크놀로지 계열 타이어 제조사.",
    "금호타이어":"타이어 전문 제조사. 중국·미국 현지 생산.",
    "에이치디씨":"HDC그룹 지주사. 건설·유통·금융 계열사 보유.",
    "이스트소프트":"알약·알집 등 보안·유틸리티 소프트웨어. AI 사업 확장 중.",
    "한화손해보험":"한화그룹 손해보험사.",
    "성창기업지주":"목재·건자재 유통 지주사.",
    "GS건설":"국내 대형 건설사. 자이 아파트 브랜드 보유.",
    "KCC":"도료·실리콘·건자재 전문 대기업. 모멘티브 실리콘 인수.",
    "세방전지":"자동차용 납축전지 전문. 에너지저장장치(ESS) 사업 확대.",
    "카카오뱅크":"인터넷 전문은행 1위. 모바일 금융 플랫폼 중심 성장.",
    "카카오페이":"카카오 간편결제·금융 플랫폼. 보험·투자 서비스 확대.",
    "SK바이오사이언스":"백신 CMO·자체 개발 바이오 기업. 코로나 이후 신규 파이프라인 구축.",
    "알테오젠":"피하주사 제형 변환 기술 독보적. 글로벌 빅파마 기술이전 다수.",
    "리가켐바이오":"항체-약물 접합체(ADC) 전문. 글로벌 ADC 플랫폼 기술이전 선도.",
    "한국타이어앤테크놀로지":"국내 1위 타이어 그룹 지주사. 전기차용 타이어 수요 확대.",
    "안랩":"국내 대표 사이버보안 기업. 백신·EDR·보안관제 서비스.",
    "현대로템":"K2 전차·수소트램 제조. 방산·철도 양대 사업 운영.",
    "한국항공우주":"KF-21·수리온 개발사. 국산 전투기·헬기 제조.",
    "이마트":"국내 1위 대형마트. SSG닷컴 통해 온라인 전환 중.",
    "GS리테일":"편의점(GS25)·슈퍼·홈쇼핑 운영. 생활유통 플랫폼.",
    "메리츠금융지주":"메리츠화재·메리츠증권 지주. 고배당·고ROE 금융그룹.",
    "메리츠화재":"손해보험사. 장기보험 중심 고수익 구조 보유.",
    "한화생명":"국내 2위 생명보험사. 한화그룹 금융 계열사.",
    "키움증권":"온라인 주식 거래 점유율 1위. 리테일 브로커리지 강자.",
    "한화솔루션":"태양광·화학 사업 영위. 큐셀 브랜드 북미 태양광 모듈 1위.",
    "HD현대미포":"중형 선박 특화 조선사. PC선·MR탱커 강자.",
    "CJ대한통운":"국내 1위 물류·택배 기업. 글로벌 물류 네트워크 확장.",
    "포스코퓨처엠":"POSCO 계열 이차전지 소재 전문사.",
    "SK바이오팜":"뇌전증 치료제 세노바메이트 개발사. 미국 직접 판매 체계 보유.",
    "휴젤":"보툴리눔 톡신 국내 1위. 중국·미국 수출 확대.",
    "종근당":"국내 중견 제약사. 케이캡·듀비에 등 자체 신약 보유.",
    "넥슨게임즈":"던전앤파이터·메이플스토리 등 IP 보유 게임사.",
    "데브시스터즈":"쿠키런 IP 보유 모바일 게임사. 글로벌 확장 중.",
    "LIG넥스원":"유도무기·레이더 등 정밀방산 전문. K-방산 수출 수혜.",
    "한화":"한화그룹 모회사. 방산·화학·유통·금융 계열사 보유.",
    "CJ":"CJ그룹 지주사. 식품·물류·엔터·바이오 사업 포트폴리오.",
    "OCI홀딩스":"태양광 폴리실리콘·화학 지주사.",
    "ASML":"반도체 노광장비 독점 공급사. EUV 장비 없이는 첨단 반도체 불가.",
    "TSMC":"파운드리 세계 1위. 애플·NVIDIA 등 빅테크 칩 위탁생산.",
    "Seagate":"HDD 세계 1위. 데이터센터 스토리지 수요 수혜.",
    "Oracle":"클라우드 ERP·데이터베이스. AI 인프라 투자로 클라우드 급성장.",
    "IBM":"엔터프라이즈 IT·AI 서비스. 하이브리드 클라우드·Watson AI.",
    "HPE":"엔터프라이즈 서버·스토리지·네트워크. AI 서버 수요 수혜.",
    "SentinelOne":"AI 기반 엔드포인트 보안. 자율 위협 탐지·대응 플랫폼.",
    "HubSpot":"중소기업용 CRM·마케팅 자동화 SaaS 1위.",
    "MongoDB":"NoSQL 데이터베이스 클라우드 서비스. 개발자 친화적 DB 플랫폼.",
    "DraftKings":"온라인 스포츠 베팅 플랫폼. 미국 합법화 수혜.",
    "Plug Power":"수소연료전지 기업. 물류센터·데이터센터 전력 공급 목표.",
    "ChargePoint":"전기차 충전 네트워크 운영사. 북미 최대 EV 충전 인프라.",
    "DexCom":"연속혈당측정기 전문. 당뇨 관리 디지털 헬스 선도.",
    "GE HealthCare":"의료영상·AI 진단 장비. GE에서 분사한 헬스케어 전문사.",
    "Hologic":"여성 건강 의료기기 전문. 유방암 진단·자궁경부암 검사 선도.",
    "Expedia":"온라인 여행 플랫폼. Hotels.com·Vrbo 등 브랜드 운영.",
    "Robinhood":"수수료 제로 주식·코인 거래 플랫폼. 개인 투자자 대상 핀테크.",
    "T-Mobile":"미국 2위 이동통신사. 5G 인프라 선도.",
    "Comcast":"미국 최대 케이블·미디어 기업. NBCUniversal·Peacock 운영.",
    "Warner Bros Discovery":"HBO·CNN·DC 콘텐츠 보유 미디어 그룹. 스트리밍 Max 운영.",
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
/* 뉴스 섹션 */
.news-wrap{margin-top:10px;border-top:1px solid #1e2235;padding-top:10px}
.news-title{font-size:11px;font-weight:700;color:#555;letter-spacing:.5px;margin-bottom:8px}
.news-item{padding:8px 0;border-bottom:1px solid #1a1d27;cursor:pointer}
.news-item:last-child{border-bottom:none}
.news-item:hover .news-headline{color:#60a5fa}
.news-headline{font-size:13px;color:#ccc;line-height:1.4;margin-bottom:4px;transition:color .15s}
.news-meta{font-size:11px;color:#444;display:flex;gap:8px}
.news-source{color:#555;font-weight:600}
.news-loading{font-size:12px;color:#555;padding:8px 0}
body.light .news-wrap{border-color:#f0f0f5}
body.light .news-item{border-color:#f5f5f7}
body.light .news-headline{color:#444}
body.light .news-meta{color:#aaa}
body.light .news-source{color:#999}
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
.indicators{display:flex;gap:8px;padding:12px 16px;overflow-x:auto;scrollbar-width:none}
.indicators::-webkit-scrollbar{display:none}
.ind-card{flex-shrink:0;background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;padding:10px 14px;min-width:96px;position:relative;overflow:hidden}
.ind-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#2563eb44,#2563eb)}
.ind-label{font-size:10px;color:#555;margin-bottom:4px;white-space:nowrap;letter-spacing:.3px}
.ind-value{font-size:16px;font-weight:700;white-space:nowrap;letter-spacing:-.3px}
.ind-chg{font-size:11px;margin-top:3px;font-weight:600}
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
.section-label{font-size:12px;font-weight:700;letter-spacing:.5px;color:#e8eaed;margin:16px 0 8px;display:flex;align-items:center;gap:8px}
.section-label-sub{font-size:11px;color:#555;font-weight:400;margin-left:auto}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.card{background:#1a1d27;border-radius:14px;border:1px solid #2a2d3a;overflow:hidden;margin-bottom:10px}
.stock-row{display:flex;align-items:center;padding:12px 14px;border-bottom:1px solid #1a1d24;cursor:pointer;transition:background .15s;gap:10px}
.stock-row:hover{background:#1e2235}
.stock-row:last-child{border-bottom:none}
.rank{font-size:12px;color:#333;width:20px;flex-shrink:0;font-weight:700}
.rank-top{color:#f59e0b}
.info{flex:0 0 130px;min-width:0}
.sname{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#e8eaed}
.sector-tag{display:inline-block;font-size:10px;padding:2px 7px;border-radius:5px;margin-top:3px;font-weight:600;letter-spacing:.2px}
.bar-wrap{flex:1;margin:0 4px}
.bar-bg{height:4px;background:#1e2235;border-radius:2px}
.bar-fill{height:4px;border-radius:2px;transition:width .4s ease}
.price{font-size:11px;color:#555;white-space:nowrap;text-align:right;min-width:60px}
.chg{font-size:15px;font-weight:700;min-width:68px;text-align:right;white-space:nowrap;letter-spacing:-.3px}
/* TOP 픽 */
.top-pick-wrap{margin:0 16px 4px}
.top-pick-header{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.top-pick-title{font-size:12px;font-weight:700;color:#e8eaed;letter-spacing:.3px}
.top-pick-badge{font-size:10px;font-weight:700;background:#2563eb22;color:#60a5fa;padding:2px 8px;border-radius:20px;border:1px solid #2563eb44}
.top-pick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.top-pick-card{background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;padding:12px 12px 10px;cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.top-pick-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.top-pick-card:hover{border-color:#2563eb88;transform:translateY(-1px)}
.top-pick-rank{font-size:10px;color:#555;font-weight:700;margin-bottom:6px}
.top-pick-name{font-size:13px;font-weight:700;color:#e8eaed;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top-pick-sector{font-size:10px;color:#666;margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top-pick-chg{font-size:18px;font-weight:700;letter-spacing:-.5px}
.top-pick-mom{font-size:10px;color:#555;margin-top:3px}
body.light .top-pick-card{background:#fff;border-color:#e5e5ea}
body.light .top-pick-name{color:#1d1d1f}
body.light .top-pick-rank{color:#aaa}
body.light .top-pick-sector{color:#aaa}
body.light .top-pick-mom{color:#bbb}
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
/* FNG 게이지 카드 */
.fng-card{flex-shrink:0;background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;padding:10px 14px;min-width:130px;position:relative;overflow:hidden}
.fng-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.fng-label{font-size:10px;color:#555;margin-bottom:4px;letter-spacing:.3px}
.fng-gauge-bg{height:5px;background:#1e2235;border-radius:3px;overflow:hidden;margin:6px 0 4px}
.fng-gauge-fill{height:5px;border-radius:3px;transition:width .5s ease}
.fng-value{font-size:16px;font-weight:700;letter-spacing:-.3px}
.fng-text{font-size:10px;margin-top:2px;font-weight:600}
.fng-prev{font-size:10px;color:#555;margin-top:2px}
body.light .fng-card{background:#fff;border-color:#e5e5ea}
/* FNG 팝업 */
.fng-popup-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:200;align-items:center;justify-content:center}
.fng-popup-overlay.show{display:flex}
.fng-popup{background:#1a1d27;border:1px solid #2a2d3a;border-radius:20px;padding:28px 24px 24px;width:90%;max-width:360px;text-align:center}
.fng-popup-title{font-size:13px;font-weight:700;color:#888;letter-spacing:.5px;margin-bottom:20px}
.fng-popup-close{position:absolute;top:12px;right:16px;background:none;border:none;color:#555;font-size:20px;cursor:pointer}
.fng-gauge-svg{width:100%;max-width:280px;margin:0 auto;display:block}
.fng-popup-num{font-size:48px;font-weight:700;margin:8px 0 4px;letter-spacing:-2px}
.fng-popup-label{font-size:16px;font-weight:600;margin-bottom:16px}
.fng-popup-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px;border-top:1px solid #2a2d3a;padding-top:16px}
.fng-stat{text-align:center}
.fng-stat-label{font-size:11px;color:#555;margin-bottom:4px}
.fng-stat-val{font-size:13px;font-weight:600;color:#e8eaed}
body.light .fng-popup{background:#fff;border-color:#e5e5ea}
body.light .fng-popup-stats{border-color:#f0f0f5}
body.light .fng-stat-val{color:#1d1d1f}
body.light .fng-gauge-bg{background:#e5e5ea}
/* 섹터 필터 */
.sector-filter-wrap{padding:8px 16px 0;display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;flex-wrap:nowrap}
.sector-filter-wrap::-webkit-scrollbar{display:none}
.sf-chip{flex-shrink:0;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid #2a2d3a;background:#1a1d27;color:#888;transition:all .2s;white-space:nowrap}
.sf-chip.active{color:#fff;border-color:transparent}
.sf-chip:hover{border-color:#2563eb}
body.light .sf-chip{background:#fff;border-color:#e5e5ea;color:#999}
body.light .sf-chip.active{color:#fff}
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
  <div class="fng-card" id="fngCard" style="display:none;cursor:pointer" onclick="openFngPopup()">
    <div class="fng-label">공포탐욕지수 ↗</div>
    <div class="fng-value" id="fngValue">—</div>
    <div class="fng-gauge-bg"><div class="fng-gauge-fill" id="fngGauge" style="width:0%"></div></div>
    <div class="fng-text" id="fngText">—</div>
    <div class="fng-prev" id="fngPrev"></div>
  </div>
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
<div class="sector-filter-wrap" id="sectorFilterWrap" style="display:none">
  <div class="sf-chip active" data-sector="전체" onclick="setSectorFilter('전체',this)" style="background:#2563eb">전체</div>
</div>

<div class="content">
  <div id="list-view">
    <!-- TOP 픽 -->
    <div class="top-pick-wrap" id="topPickWrap" style="display:none">
      <div class="top-pick-header">
        <span class="top-pick-title">⚡ 오늘의 TOP 픽</span>
        <span class="top-pick-badge" id="topPickMarket">코스피</span>
      </div>
      <div class="top-pick-grid" id="topPickGrid"></div>
    </div>
    <div class="section-label" style="margin-top:14px">
      <span class="dot" style="background:#22c55e"></span>상위 상승
      <span class="section-label-sub" id="upCount"></span>
    </div>
    <div class="card" id="up-list"></div>
    <div class="section-label">
      <span class="dot" style="background:#ef4444"></span>상위 하락
      <span class="section-label-sub" id="dnCount"></span>
    </div>
    <div class="card" id="down-list"></div>
  </div>
  <div id="heatmap-view" style="display:none">
    <div class="sector-trend-box" id="sectorTrendWrap">
      <div class="sector-trend-title" id="sectorTrendTitle">📊 오늘 섹터별 등락률</div>
      <canvas class="sector-trend-canvas" id="sectorTrendCanvas" height="160" style="display:none"></canvas>
    </div>
    <div class="heatmap" id="heatmap-grid"></div>
  </div>
  <div class="updated" id="updatedAt"></div>
</div>

<!-- FNG 팝업 -->
<div class="fng-popup-overlay" id="fngPopupOverlay" onclick="if(event.target===this)this.classList.remove('show')">
  <div class="fng-popup" style="position:relative">
    <button class="fng-popup-close" onclick="document.getElementById('fngPopupOverlay').classList.remove('show')">×</button>
    <div class="fng-popup-title">CNN FEAR & GREED INDEX</div>
    <svg class="fng-gauge-svg" viewBox="0 0 200 110" id="fngSvg"></svg>
    <div class="fng-popup-num" id="fngPopupNum">—</div>
    <div class="fng-popup-label" id="fngPopupLabel">—</div>
    <div class="fng-popup-stats" id="fngPopupStats"></div>
  </div>
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
    <!-- 관련 뉴스 -->
    <div class="news-wrap" id="popupNews" style="display:none">
      <div class="news-title">📰 관련 뉴스</div>
      <div id="newsItems"></div>
    </div>
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
let data=null,market='kospi',view='list',dates=[],currentDate='',allData={},_sectorFilter='전체';
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

function switchMarket(m,el){market=m;_sectorFilter='전체';document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');render();loadAISummary();}
function switchView(v,el){
  view=v;
  document.querySelectorAll('.view-tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('list-view').style.display=v==='list'?'':'none';
  document.getElementById('heatmap-view').style.display=v==='heatmap'?'':'none';
  const fw=document.getElementById('sectorFilterWrap');
  if(fw)fw.style.display=v==='list'?'flex':'none';
  render();
  if(v==='heatmap') setTimeout(renderSectorTrend, 80);
}

function buildSectorFilter(){
  const fw=document.getElementById('sectorFilterWrap');
  if(!fw||!data)return;
  const sectors=[...new Set([
    ...(data[market+'_up']||[]).map(s=>s.sector),
    ...(data[market+'_down']||[]).map(s=>s.sector)
  ].filter(Boolean))].sort();
  const chips=[{s:'전체',col:'#2563eb'},...sectors.map(s=>({s,col:SECTOR_COLORS[s]||'#6b7280'}))];
  fw.innerHTML=chips.map(({s,col})=>{
    const isActive=_sectorFilter===s;
    const bg=isActive?col:'';
    const border=isActive?'transparent':'';
    const color=isActive?'#fff':'#888';
    return `<div class="sf-chip${isActive?' active':''}" data-sector="${s}" onclick="setSectorFilter('${s}',this)" style="${isActive?`background:${col};border-color:transparent`:''}">${s}</div>`;
  }).join('');
}

function setSectorFilter(sector,el){
  // 이미 선택된 섹터 다시 누르면 전체로 토글
  if(_sectorFilter===sector && sector!=='전체') sector='전체';
  _sectorFilter=sector;
  document.querySelectorAll('.sf-chip').forEach(c=>{
    const s=c.dataset.sector;
    const col=s==='전체'?'#2563eb':SECTOR_COLORS[s]||'#6b7280';
    const isActive=s===sector;
    c.classList.toggle('active',isActive);
    c.style.background=isActive?col:'';
    c.style.borderColor=isActive?'transparent':'';
    c.style.color=isActive?'#fff':'#888';
  });
  renderList();
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

// 팝업 - el은 DOM 엘리먼트(data-stock attr) 또는 stock 객체 직접 가능
function openPopup(el){
  const s=typeof el.getAttribute==='function'
    ? JSON.parse(el.getAttribute('data-stock')||'{}')
    : el;
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
  // 뉴스 로드
  loadStockNews(s.name||s.ticker||'', s.ticker||'', market);
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

// 종목 관련 뉴스
async function loadStockNews(name, ticker, mkt){
  const wrap  = document.getElementById('popupNews');
  const items = document.getElementById('newsItems');
  if(!wrap||!items) return;
  wrap.style.display = 'block';
  items.innerHTML = '<div class="news-loading">뉴스 불러오는 중...</div>';
  try{
    const params = new URLSearchParams({name, ticker, market:mkt});
    const res = await fetch('/api/news?'+params);
    const news = await res.json();
    if(!news.length){
      items.innerHTML = '<div class="news-loading">관련 뉴스 없음</div>';
      return;
    }
    items.innerHTML = news.map(n=>`
      <div class="news-item" onclick="window.open('${n.link}','_blank')">
        <div class="news-headline">${n.title}</div>
        <div class="news-meta">
          <span class="news-source">${n.source||''}</span>
          <span>${n.pub||''}</span>
        </div>
      </div>`).join('');
  }catch(e){
    items.innerHTML = '<div class="news-loading">뉴스 로드 실패</div>';
  }
}

// 섹터 흐름 추이 차트
function renderSectorTrend(){
  const wrap=document.getElementById('sectorTrendWrap');
  const titleEl=document.getElementById('sectorTrendTitle');
  if(!wrap)return;
  wrap.style.display='block';

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
  if(!latestSectors.length){wrap.style.display='none';return;}

  const hasEnoughData=dates.length>=3&&Object.values(sectorMap).some(pts=>pts.length>=3);

  let chartEl=document.getElementById('sectorTrendHtml');
  if(!chartEl){
    chartEl=document.createElement('div');
    chartEl.id='sectorTrendHtml';
    wrap.appendChild(chartEl);
  }
  chartEl.style.cssText='width:100%;padding:4px 0 0';

  // ── 바차트 (데이터 부족) ──
  if(!hasEnoughData){
    if(titleEl)titleEl.textContent='📊 오늘 섹터별 등락률';
    const sorted=[...latestSectors].sort((a,b)=>b.avg_chg-a.avg_chg);
    const show=[...sorted.slice(0,4),...sorted.slice(-4)].filter((s,i,a)=>a.findIndex(x=>x.sector===s.sector)===i);
    const maxAbs=Math.max(...show.map(s=>Math.abs(s.avg_chg)),0.5);
    chartEl.innerHTML=show.map(sec=>{
      const isUp=sec.avg_chg>=0;
      const col=SECTOR_COLORS[sec.sector]||(isUp?'#22c55e':'#ef4444');
      const pct=Math.round(Math.abs(sec.avg_chg)/maxAbs*50);
      const chgStr=(isUp?'+':'')+sec.avg_chg+'%';
      return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
        <div style="flex:0 0 80px;font-size:12px;color:#aaa;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${sec.sector}</div>
        <div style="flex:1;height:16px;background:#1e2235;border-radius:3px;overflow:hidden;position:relative">
          <div style="position:absolute;${isUp?'left:0':'right:0'};top:0;height:100%;width:${pct}%;background:${col}55;border-radius:3px"></div>
          <div style="position:absolute;${isUp?'left:0':'right:0'};top:0;height:100%;width:3px;background:${col}"></div>
        </div>
        <div style="flex:0 0 54px;font-size:12px;font-weight:700;color:${col}">${chgStr}</div>
      </div>`;
    }).join('');
    return;
  }

  // ── 라인차트 (3일 이상) — HTML 테이블 방식으로 레이블 겹침 없이 ──
  if(titleEl)titleEl.textContent='📈 섹터 흐름 추이';

  // 상승 상위 2 + 하락 상위 2
  const byUp=[...latestSectors].sort((a,b)=>b.avg_chg-a.avg_chg);
  const byDn=[...latestSectors].sort((a,b)=>a.avg_chg-b.avg_chg);
  const topSectors=[...new Set([byUp[0]?.sector,byUp[1]?.sector,byDn[0]?.sector,byDn[1]?.sector].filter(Boolean))].slice(0,4);

  const allVals=topSectors.flatMap(sec=>(sectorMap[sec]||[]).map(p=>p.avg));
  if(!allVals.length)return;
  const minV=Math.min(...allVals,-0.5),maxV=Math.max(...allVals,0.5);
  const range=maxV-minV||1;

  const palette=['#22c55e','#3b82f6','#ef4444','#f97316'];
  const colors=topSectors.map((sec,i)=>SECTOR_COLORS[sec]||palette[i%4]);

  // SVG 크기 — 레이블을 아래 별도 행으로 분리해서 겹침 제거
  const W=360,H=120;
  const pad={t:10,b:18,l:6,r:6};
  const toX=(j,total)=>pad.l+(j/(Math.max(total-1,1)))*(W-pad.l-pad.r);
  const toY=v=>pad.t+(1-(v-minV)/range)*(H-pad.t-pad.b);
  const y0=toY(0);

  let svgLines=`<line x1="${pad.l}" y1="${y0}" x2="${W-pad.r}" y2="${y0}" stroke="#2a2d3a" stroke-width="1" stroke-dasharray="4,3"/>`;

  topSectors.forEach((sec,i)=>{
    const pts=(sectorMap[sec]||[]).filter(p=>p.avg!=null);
    if(pts.length<2)return;
    const col=colors[i];
    const pointStr=pts.map((p,j)=>`${toX(j,pts.length)},${toY(p.avg)}`).join(' ');
    svgLines+=`<polyline points="${pointStr}" fill="none" stroke="${col}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
    const lx=toX(pts.length-1,pts.length);
    const ly=toY(pts[pts.length-1].avg);
    svgLines+=`<circle cx="${lx}" cy="${ly}" r="3.5" fill="${col}"/>`;
  });

  // x축
  const refSec=topSectors.find(s=>(sectorMap[s]||[]).length>=2);
  let xLabels='';
  if(refSec){
    const pts=sectorMap[refSec];
    const idxs=[0,...(pts.length>2?[Math.floor(pts.length/2)]:[]),pts.length-1];
    idxs.forEach(i=>{
      if(!pts[i])return;
      xLabels+=`<text x="${toX(i,pts.length)}" y="${H-2}" font-size="10" fill="#777" text-anchor="middle" font-family="-apple-system,sans-serif">${pts[i].d.slice(5)}</text>`;
    });
  }

  // 레이블 행 — 겹침 없이 flex로 나열
  const labelRow=topSectors.map((sec,i)=>{
    const pts=(sectorMap[sec]||[]).filter(p=>p.avg!=null);
    if(!pts.length)return '';
    const last=pts[pts.length-1];
    const col=colors[i];
    const chgStr=last.avg>=0?'+'+last.avg+'%':last.avg+'%';
    const short=sec.length>6?sec.slice(0,5)+'..':sec;
    return `<div style="display:flex;align-items:center;gap:4px;font-size:11px;white-space:nowrap">
      <span style="width:8px;height:8px;border-radius:50%;background:${col};flex-shrink:0;display:inline-block"></span>
      <span style="color:#aaa">${short}</span>
      <span style="color:${col};font-weight:700">${chgStr}</span>
    </div>`;
  }).join('');

  chartEl.innerHTML=
    `<svg viewBox="0 0 ${W} ${H}" width="100%" style="display:block;overflow:visible">${svgLines}${xLabels}</svg>`+
    `<div style="display:flex;flex-wrap:wrap;gap:8px 14px;margin-top:8px;padding:0 4px">${labelRow}</div>`;
}
function renderTopPick(){
  const wrap=document.getElementById('topPickWrap');
  const grid=document.getElementById('topPickGrid');
  const badge=document.getElementById('topPickMarket');
  if(!wrap||!grid||!data)return;
  const all=[...(data[market+'_up']||[]),...(data[market+'_down']||[])];
  const picks=all.filter(s=>s.momentum!=null).sort((a,b)=>b.momentum-a.momentum).slice(0,3);
  if(!picks.length){wrap.style.display='none';return;}
  wrap.style.display='block';
  badge.textContent=market==='kospi'?'코스피':'나스닥';
  const colors=['#f59e0b','#94a3b8','#b45309'];
  const labels=['1위','2위','3위'];
  grid.innerHTML=picks.map((s,i)=>{
    const nm=s.name||s.ticker||'';const sec=s.sector||'';
    const col=SECTOR_COLORS[sec]||'#2563eb';
    const isUp=s.chg_pct>=0;
    const chgCol=isUp?'#22c55e':'#ef4444';
    const sd=JSON.stringify(s).replace(/"/g,'&quot;');
    const mom=s.momentum>0?'+'+s.momentum:s.momentum;
    return '<div class="top-pick-card" onclick="openPopup(this)" data-stock="'+sd+'" style="border-top-color:'+colors[i]+'">'
      +'<div class="top-pick-rank" style="color:'+colors[i]+'">'+labels[i]+'</div>'
      +'<div class="top-pick-name">'+nm+'</div>'
      +'<div class="top-pick-sector">'+sec+'</div>'
      +'<div class="top-pick-chg '+( isUp?'up':'down')+'">'+( isUp?'+':'')+s.chg_pct+'%</div>'
      +'<div class="top-pick-mom">모멘텀 '+mom+'</div>'
      +'</div>';
  }).join('');
}

function renderList(){
  const allUp=data[market+'_up']||[],allDn=data[market+'_down']||[];
  const up=_sectorFilter==='전체'?allUp:allUp.filter(s=>s.sector===_sectorFilter);
  const dn=_sectorFilter==='전체'?allDn:allDn.filter(s=>s.sector===_sectorFilter);
  const max=Math.max(...[...allUp,...allDn].map(s=>Math.abs(s.chg_pct)),1);
  const upCnt=document.getElementById('upCount');
  const dnCnt=document.getElementById('dnCount');
  const filterLabel=_sectorFilter==='전체'?up.length+'종목':`${_sectorFilter} ${up.length}종목`;
  if(upCnt)upCnt.textContent=filterLabel;
  if(dnCnt)dnCnt.textContent=_sectorFilter==='전체'?dn.length+'종목':`${_sectorFilter} ${dn.length}종목`;
  buildSectorFilter();
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
      const rankCls=i<3?' rank-top':'';
      const rankSymbol=i===0?'①':i===1?'②':i===2?'③':(i+1);
      return '<div class="stock-row" onclick="openPopup(this)" data-stock="'+sd+'">'
        +'<div class="rank'+rankCls+'">'+rankSymbol+'</div>'
        +'<div class="info"><div class="sname">'+nm+' '+badges+'</div>'
        +'<span class="sector-tag" style="background:'+col+'22;color:'+col+'">'+sec+'</span></div>'
        +'<div class="bar-wrap"><div class="bar-bg"><div class="bar-fill" style="width:'+pct+'%;background:'+(isUp?'#22c55e':'#ef4444')+'"></div></div></div>'
        +'<div class="price">'+price+'</div>'
        +'<div class="chg '+(isUp?'up':'down')+'">'+(isUp?'+':'')+s.chg_pct+'%</div>'
        +'</div>';
    }).join('');
  }
  document.getElementById('up-list').innerHTML=rows(up,true);
  document.getElementById('down-list').innerHTML=rows(dn,false);
  renderTopPick();
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

function selectDate(d){
  currentDate=d;
  data=allData[d]||null;
  if(data) setIndexFromData(data);
  if(data) setFNG(data.fng, data.fng_label, data.fng_prev);
  renderDateBar();render();loadAISummary();
  if(view==='heatmap') setTimeout(renderSectorTrend,80);
}

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
    // 코스피/나스닥 지수는 market_data.json 값 우선 사용 (loadAll에서 처리)
  }catch(e){}
}

function setIndexFromData(d){
  function setIdx(id,val,chg){
    if(!val)return;const isUp=chg>=0;
    document.getElementById(id).textContent=val.toLocaleString();
    const el=document.getElementById(id+'-c');
    el.textContent=(isUp?'+':'')+chg+'%';el.className='ind-chg '+(isUp?'up':'down');
  }
  setIdx('kospi-idx',d.kospi_index,d.kospi_chg);
  setIdx('nasdaq-idx',d.nasdaq_index,d.nasdaq_chg);
}

let _fngData = {value:null, label:null, prev:null};

function openFngPopup(){
  if(_fngData.value == null) return;
  const fng = _fngData.value;
  const col = fng<=25?'#ef4444':fng<=45?'#f97316':fng<=55?'#eab308':fng<=75?'#22c55e':'#00d084';
  const labelKo = fng<=25?'극도의 공포':fng<=45?'공포':fng<=55?'중립':fng<=75?'탐욕':'극도의 탐욕';

  // SVG 반원 게이지
  const svg = document.getElementById('fngSvg');
  const cx=100, cy=100, r=80;
  // 배경 아크 구간 (5색)
  const zones = [
    {from:0,to:25,col:'#ef4444'},
    {from:25,to:45,col:'#f97316'},
    {from:45,to:55,col:'#eab308'},
    {from:55,to:75,col:'#22c55e'},
    {from:75,to:100,col:'#00d084'},
  ];
  function polar(deg, radius){
    const rad = (180 - deg * 1.8) * Math.PI / 180;
    return [cx + radius * Math.cos(rad), cy - radius * Math.sin(rad)];
  }
  function arc(from, to, r, col){
    const [x1,y1] = polar(from, r);
    const [x2,y2] = polar(to, r);
    const large = (to - from) > 50 ? 1 : 0;
    return `<path d="M${x1} ${y1} A${r} ${r} 0 ${large} 0 ${x2} ${y2}" fill="none" stroke="${col}" stroke-width="16" stroke-linecap="butt"/>`;
  }
  // 바늘
  const [nx,ny] = polar(fng, 60);
  const needle = `<line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="white" stroke-width="3" stroke-linecap="round"/>
    <circle cx="${cx}" cy="${cy}" r="5" fill="white"/>`;
  // 라벨
  const ticks = [
    {v:0,label:'0'},{v:25,label:'25'},{v:50,label:'50'},{v:75,label:'75'},{v:100,label:'100'}
  ];
  const ticksSvg = ticks.map(t=>{
    const [tx,ty]=polar(t.v,95);
    return `<text x="${tx}" y="${ty}" text-anchor="middle" dominant-baseline="middle" font-size="8" fill="#666">${t.label}</text>`;
  }).join('');
  svg.innerHTML = zones.map(z=>arc(z.from,z.to,80,z.col)).join('') + ticksSvg + needle;

  document.getElementById('fngPopupNum').textContent = fng;
  document.getElementById('fngPopupNum').style.color = col;
  document.getElementById('fngPopupLabel').textContent = labelKo;
  document.getElementById('fngPopupLabel').style.color = col;

  // 통계
  const prev = _fngData.prev;
  const diff = prev != null ? fng - prev : null;
  const prevLabelKo = prev!=null?(prev<=25?'극공포':prev<=45?'공포':prev<=55?'중립':prev<=75?'탐욕':'극탐욕'):'—';
  document.getElementById('fngPopupStats').innerHTML =
    `<div class="fng-stat"><div class="fng-stat-label">전일 종가</div><div class="fng-stat-val">${prev??'—'} ${prevLabelKo}</div></div>` +
    `<div class="fng-stat"><div class="fng-stat-label">전일 대비</div><div class="fng-stat-val" style="color:${diff!=null&&diff>=0?'#22c55e':'#ef4444'}">${diff!=null?(diff>=0?'+':'')+diff:'—'}</div></div>`;

  document.getElementById('fngPopupOverlay').classList.add('show');
}

function setFNG(fng, label, prev){
  _fngData = {value:fng, label:label, prev:prev};
  const card = document.getElementById('fngCard');
  if(!card || fng == null) return;
  card.style.display = 'block';

  // 색상: 0-25 극공포(빨강), 26-45 공포(주황), 46-55 중립(노랑), 56-75 탐욕(연초록), 76-100 극탐욕(초록)
  const col = fng<=25?'#ef4444':fng<=45?'#f97316':fng<=55?'#eab308':fng<=75?'#86efac':'#22c55e';
  const emoji = fng<=25?'😱':fng<=45?'😰':fng<=55?'😐':fng<=75?'😊':'🤑';
  const labelKo = fng<=25?'극도의 공포':fng<=45?'공포':fng<=55?'중립':fng<=75?'탐욕':'극도의 탐욕';

  card.style.borderTopColor = col;
  card.querySelector('.fng-card::before');

  document.getElementById('fngValue').textContent = fng;
  document.getElementById('fngValue').style.color = col;
  document.getElementById('fngGauge').style.width = fng + '%';
  document.getElementById('fngGauge').style.background = col;
  document.getElementById('fngText').textContent = emoji + ' ' + labelKo;
  document.getElementById('fngText').style.color = col;

  if(prev != null){
    const diff = fng - prev;
    const diffStr = (diff >= 0 ? '+' : '') + diff;
    document.getElementById('fngPrev').textContent = '전일 대비 ' + diffStr;
  }

  // 카드 상단 컬러 라인
  card.style.setProperty('--fng-color', col);
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
    chip.innerHTML='<span class="fav-name">'+f.name+'</span>'+(chgStr?'<span class="fav-chg" style="color:'+col+'">'+chgStr+'</span>':'')+'<span class="fav-x" style="color:#555;font-size:14px;padding:0 4px;cursor:pointer">×</span>';
    if(found){
      chip.onclick=(e)=>{if(!e.target.classList.contains('fav-x'))openPopup(found);};
    }
    chip.querySelector('.fav-x').onclick=e=>{e.stopPropagation();_favs=_favs.filter(f2=>f2.key!==f.key);localStorage.setItem('favs',JSON.stringify(_favs));renderFavBar();};
    tab.appendChild(chip);
  });
}

async function loadAll(){
  try{
    const r=await fetch('/api/history');const h=await r.json();
    dates=h.dates||[];allData=h.data||{};
    currentDate=dates[dates.length-1]||'';
    data=allData[currentDate]||null;
    if(data) setIndexFromData(data);
    if(data) setFNG(data.fng, data.fng_label, data.fng_prev);
    const fw=document.getElementById('sectorFilterWrap');
    if(fw)fw.style.display='flex';
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
        print(f"indicators 오류: {e}")
    return jsonify(result)

# 메모리 캐시: {"{date}_{market}": "요약 텍스트"}
_summary_cache = {}

@app.route("/api/cache/clear")
def api_cache_clear():
    _summary_cache.clear()
    _brief_cache.clear()
    print("[캐시 전체 초기화]")
    return jsonify({"ok": True, "message": "캐시 초기화 완료"})

@app.route("/api/summary")
def api_summary():
    market = request.args.get("market", "kospi")
    date   = request.args.get("date", "")
    data   = None
    if date: data = fetch_from_github(f"history/{date}.json")
    if not data: data = fetch_from_github("market_data.json")
    if not data: return jsonify({"summary": "데이터 없음"})

    actual_date = data.get("date", date)
    cache_key   = f"{actual_date}_{market}"

    # 캐시 히트 → 토큰 0 소비
    if cache_key in _summary_cache:
        print(f"[캐시 히트] {cache_key}")
        return jsonify({"summary": _summary_cache[cache_key], "cached": True})

    up          = data.get(f"{market}_up",   [])[:5]
    down        = data.get(f"{market}_down", [])[:5]
    sectors     = data.get(f"{market}_sectors", [])
    market_name = "코스피" if market == "kospi" else "나스닥"
    up_str      = ", ".join([f"{s.get('name',s.get('ticker',''))}({s['chg_pct']:+.1f}%)" for s in up])
    down_str    = ", ".join([f"{s.get('name',s.get('ticker',''))}({s['chg_pct']:+.1f}%)" for s in down])
    sector_str  = ", ".join([f"{s['sector']}({s['avg_chg']:+.1f}%)" for s in sectors[:5]])

    prompt = f"""{actual_date} {market_name} 시장입니다.
상승: {up_str}
하락: {down_str}
섹터: {sector_str}

위 데이터를 바탕으로 딱 3문장만 써주세요. 각 문장은 반드시 마침표로 끝내고, 3문장이 끝나면 절대 더 쓰지 마세요. 마크다운 기호 없이 plain text로만."""

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"summary": f"{market_name} 상승 주도: {up_str} / 하락: {down_str}"})
    try:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 350,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=payload,
            headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read())
        text = res["content"][0]["text"]
        _summary_cache[cache_key] = text  # 캐시 저장
        print(f"[캐시 저장] {cache_key}")
        return jsonify({"summary": text, "cached": False})
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'read'): error_msg = e.read().decode('utf-8')
        print(f"Claude API 호출 에러: {error_msg}")
        return jsonify({"summary": f"{market_name} 상승 주도: {up_str} / 하락: {down_str}"})

_brief_cache = {}

@app.route("/api/stock_brief")
def api_stock_brief():
    name   = request.args.get("name","")
    ticker = request.args.get("ticker","")
    sector = request.args.get("sector","")
    chg    = request.args.get("chg","0")
    market = request.args.get("market","kospi")
    market_name = "코스피" if market == "kospi" else "나스닥"
    today  = datetime.now().strftime("%Y-%m-%d")

    # 캐시 키: 날짜 + 티커 (같은 날 같은 종목은 재사용)
    cache_key = f"{today}_{ticker or name}"
    if cache_key in _brief_cache:
        print(f"[brief 캐시 히트] {cache_key}")
        return jsonify({"brief": _brief_cache[cache_key], "cached": True})

    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if not api_key:
        return jsonify({"brief":"API 키가 없어 분석을 생성할 수 없습니다."})

    prompt = f"""오늘 {name}({ticker}) 종목이 {chg}% 등락했습니다.
섹터: {sector} | 시장: {market_name}

마크다운 기호 없이 plain text로, 4문장 이내로 작성하세요:
1. 이 등락의 가능한 배경 (1~2문장)
2. {sector} 섹터 내 포지션과 투자자 관점 (1문장)
3. 단기 리스크 또는 기회 요인 (1문장)"""

    try:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 250,
            "messages": [{"role":"user","content":prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read())
        text = res["content"][0]["text"]
        _brief_cache[cache_key] = text  # 캐시 저장
        print(f"[brief 캐시 저장] {cache_key}")
        return jsonify({"brief": text, "cached": False})
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


@app.route("/api/news")
def api_news():
    name   = request.args.get("name","")
    ticker = request.args.get("ticker","")
    market = request.args.get("market","kospi")
    import xml.etree.ElementTree as ET
    results = []
    query = name if market == "kospi" else (ticker + " stock")
    if not query: return jsonify([])

    sources = []
    # 1순위: 네이버 금융 뉴스 RSS (코스피)
    if market == "kospi":
        encoded = urllib.request.quote(name)
        sources.append(f"https://finance.naver.com/news/news_search.naver?rcdate=&q={encoded}&x=0&y=0")
    # 네이버 뉴스 검색 RSS
    encoded = urllib.request.quote(query)
    sources.append(f"https://openapi.naver.com/v1/search/news.json?query={encoded}&display=10&sort=date")
    # 구글 뉴스 RSS fallback
    lang = "ko" if market == "kospi" else "en"
    gl   = "KR"  if market == "kospi" else "US"
    q_enc = urllib.request.quote(query + (" 주가" if market=="kospi" else ""))
    sources.append(f"https://news.google.com/rss/search?q={q_enc}&hl={lang}&gl={gl}&ceid={gl}:{lang}")

    tried_urls = []
    for rss_url in sources[-1:]:  # 구글 뉴스 RSS만 사용 (네이버는 API 키 필요)
        tried_urls.append(rss_url)
        try:
            req = urllib.request.Request(rss_url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
            tree = ET.fromstring(raw)
            items = tree.findall(".//item")
            name_lower   = name.lower()
            ticker_lower = ticker.lower()
            seen = set()
            for item in items[:15]:
                title = item.findtext("title","").strip()
                # <title> 안에 CDATA 처리
                title = title.replace("<![CDATA[","").replace("]]>","").strip()
                link  = item.findtext("link","").strip()
                pub   = item.findtext("pubDate","").strip()
                source_el = item.find("{https://news.google.com/rss}source")
                source = source_el.text if source_el is not None else ""
                if not title or title in seen: continue
                tl = title.lower()
                # 필터: 종목명 앞 2글자 이상 또는 티커 포함
                match = (
                    name_lower in tl or
                    ticker_lower in tl or
                    (market=="kospi" and len(name)>=2 and name[:2] in title) or
                    (market=="nasdaq" and ticker and ticker.lower() in tl)
                )
                if not match: continue
                seen.add(title)
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(pub)
                    pub_str = dt.strftime("%m/%d %H:%M")
                except:
                    pub_str = pub[:10] if pub else ""
                results.append({"title":title,"link":link,"pub":pub_str,"source":source})
                if len(results) >= 4: break
            if results: break
        except Exception as e:
            print(f"뉴스 RSS 오류 ({rss_url[:60]}): {e}")

    print(f"뉴스 결과: {len(results)}건 (쿼리: {query})")
    return jsonify(results)


def manifest():
    m={"name":"데일리 마켓 브리핑","short_name":"마켓 브리핑","description":"코스피·나스닥 주도 종목 실시간 분석","start_url":"/","display":"standalone","background_color":"#0f1117","theme_color":"#0f1117","orientation":"portrait","icons":[{"src":"/icon.svg","sizes":"192x192","type":"image/svg+xml"},{"src":"/icon.svg","sizes":"512x512","type":"image/svg+xml"}]}
    return Response(json.dumps(m),mimetype="application/json")

@app.route("/ping")
def ping():
    return Response("ok", mimetype="text/plain")

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
