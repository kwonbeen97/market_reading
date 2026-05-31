# 📈 코스피 & 나스닥 주도 종목 대시보드

## 배포 방법 (무료)

### 1단계: GitHub에 올리기
1. github.com 회원가입
2. 새 저장소(repository) 만들기
3. 이 폴더 파일들을 모두 업로드

### 2단계: Render.com 배포
1. render.com 회원가입 (GitHub 계정으로 로그인)
2. "New Web Service" 클릭
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. "Deploy" 클릭 → 완료!

### 3단계: 자동 데이터 수집
- GitHub Actions가 평일 자동으로 fetch_data.py 실행
- Render가 자동으로 최신 데이터 반영

## 파일 구조
- app.py          → Flask 웹 서버
- fetch_data.py   → 데이터 수집 스크립트
- requirements.txt → 라이브러리 목록
- .github/workflows/daily.yml → 자동 스케줄러
