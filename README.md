# 📰 Morning News Digest

> AI/테크 트렌드 + 주식/시장 뉴스를 매일 아침 자동으로 요약해서 이메일로 받아보는 파이썬 자동화 프로젝트

## 📌 프로젝트 개요

금융권 데이터분석가로서 매일 AI 트렌드와 시장 동향을 빠르게 파악하기 위해 제작했습니다.
RSS 피드에서 글로벌 뉴스를 수집하고, Claude API로 요약·인사이트를 추출해 HTML 이메일로 자동 발송합니다.

## 🛠 기술 스택

| 역할 | 라이브러리 |
|---|---|
| 뉴스 수집 | `feedparser` (RSS) |
| AI 요약 | `anthropic` (Claude API) |
| 이메일 발송 | `smtplib` + Gmail SMTP |
| 스케줄링 | GitHub Actions (매일 오전 7시) |

## ⚙️ 실행 방법

### 1. 패키지 설치
```bash
pip install feedparser anthropic
```

### 2. 환경변수 설정
`.env` 파일 생성 또는 터미널에서 설정:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # Claude API 키
export SENDER_EMAIL="your@gmail.com"      # 발신 Gmail
export SENDER_APP_PW="xxxx xxxx xxxx"     # Gmail 앱 비밀번호 (아래 참고)
export RECEIVER_EMAIL="your@gmail.com"    # 수신 이메일
```

> **Gmail 앱 비밀번호 발급:**
> Google 계정 → 보안 → 2단계 인증 ON → 앱 비밀번호 생성

### 3. 실행
```bash
python news_digest.py
```

## ⏰ 매일 자동 실행 (GitHub Actions)

`.github/workflows/daily_digest.yml` 파일 생성:

```yaml
name: Daily News Digest

on:
  schedule:
    - cron: '0 22 * * *'  # 한국시간 오전 7시 (UTC 22:00 전날)
  workflow_dispatch:        # 수동 실행도 가능

jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install feedparser anthropic
      - run: python news_digest.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SENDER_EMAIL:      ${{ secrets.SENDER_EMAIL }}
          SENDER_APP_PW:     ${{ secrets.SENDER_APP_PW }}
          RECEIVER_EMAIL:    ${{ secrets.RECEIVER_EMAIL }}
```

GitHub 레포 → Settings → Secrets에 환경변수 등록하면 끝!

## 📧 이메일 예시

```
[Daily Digest] AI·시장 브리핑 04/24

■ AI/테크 트렌드
  • 핵심 트렌드: OpenAI, 새로운 멀티모달 모델 공개...
  • 주목할 포인트: 금융 자동화 영역 확대 가능성...
  • 오늘의 키워드: #LLM #멀티모달 #금융AI

■ 주식/시장 동향
  • 핵심 트렌드: 미 연준 금리 동결 시사...
  • 주목할 포인트: 테크주 반등 흐름...
  • 오늘의 키워드: #연준 #금리 #나스닥
```

## 🔧 커스터마이징

`news_digest.py` 상단의 `RSS_FEEDS` 딕셔너리에 원하는 RSS URL을 추가하면 됩니다.

```python
RSS_FEEDS = {
    "AI/테크 트렌드": [
        "https://feeds.feedburner.com/venturebeat/SZYF",
        # 추가하고 싶은 RSS URL
    ],
    "주식/시장 동향": [
        "https://feeds.finance.yahoo.com/rss/...",
        # 추가하고 싶은 RSS URL
    ],
}
```

## 💡 향후 개선 아이디어

- [ ] 네이버 금융 뉴스 크롤링 추가 (국내 시장)
- [ ] 감성 점수 시각화 차트 첨부
- [ ] Slack/카카오톡 알림 연동
- [ ] 종목별 뉴스 필터링 기능
