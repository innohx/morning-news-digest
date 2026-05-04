"""
Morning News Digest — AI/Tech & Market Daily Brief
----------------------------------------------------
매일 아침 AI/테크 트렌드 + 주식/시장 뉴스를 수집하고
Claude API로 요약해서 이메일로 발송하는 자동화 스크립트

포트폴리오: github.com/YOUR_ID/morning-news-digest
"""

import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import anthropic

# ─────────────────────────────────────────────
# 설정 (환경변수로 관리 — 코드에 직접 넣지 말 것!)
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")   # Claude API 키
SENDER_EMAIL      = os.environ.get("SENDER_EMAIL")         # 발신 Gmail 주소
SENDER_APP_PW     = os.environ.get("SENDER_APP_PW")        # Gmail 앱 비밀번호
RECEIVER_EMAIL    = os.environ.get("RECEIVER_EMAIL")       # 수신 이메일 주소


# ─────────────────────────────────────────────
# RSS 피드 목록
# ─────────────────────────────────────────────
RSS_FEEDS = {
    "AI/테크 트렌드": [
        "https://feeds.feedburner.com/venturebeat/SZYF",       # VentureBeat AI
        "https://techcrunch.com/feed/",                        # TechCrunch
        "https://www.theverge.com/rss/index.xml",              # The Verge
    ],
    "주식/시장 동향": [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",  # Yahoo Finance S&P500
        "https://www.investing.com/rss/news.rss",              # Investing.com
        "https://feeds.bloomberg.com/markets/news.rss",        # Bloomberg Markets
    ],
}

MAX_ARTICLES_PER_CATEGORY = 5  # 카테고리별 최대 기사 수


# ─────────────────────────────────────────────
# 1. 뉴스 수집
# ─────────────────────────────────────────────
def fetch_news(feeds: dict, max_per_category: int = 5) -> dict:
    """RSS 피드에서 최신 기사 제목 + 링크를 수집합니다."""
    result = {}

    for category, urls in feeds.items():
        articles = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:max_per_category]:
                    articles.append({
                        "title":   entry.get("title", "제목 없음").strip(),
                        "link":    entry.get("link", ""),
                        "summary": entry.get("summary", "")[:300],  # 요약 미리보기 (300자)
                    })
                    if len(articles) >= max_per_category:
                        break
            except Exception as e:
                print(f"[RSS 수집 오류] {url}: {e}")

        result[category] = articles[:max_per_category]

    return result


# ─────────────────────────────────────────────
# 2. Claude API로 뉴스 요약
# ─────────────────────────────────────────────
def summarize_with_claude(news_data: dict) -> dict:
    """카테고리별 기사 목록을 Claude로 요약합니다."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    summaries = {}

    for category, articles in news_data.items():
        if not articles:
            summaries[category] = "수집된 기사가 없습니다."
            continue

        # 프롬프트 구성
        articles_text = "\n".join([
            f"{i+1}. {a['title']}\n   {a['summary']}"
            for i, a in enumerate(articles)
        ])

        prompt = f"""당신은 금융권 데이터분석가를 위한 뉴스 큐레이터입니다.
아래 [{category}] 기사들을 읽고, 다음 형식으로 요약해주세요.

[요약 형식]
• 핵심 트렌드 2~3줄 요약 (가장 중요한 흐름)
• 주목할 포인트: (금융/데이터 분석 관점에서 의미 있는 내용)
• 오늘의 키워드: #키워드1 #키워드2 #키워드3

[기사 목록]
{articles_text}

간결하고 인사이트 있게 작성해주세요. 전문 용어는 유지하되 핵심만 담아주세요."""

        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            summaries[category] = response.content[0].text
        except Exception as e:
            summaries[category] = f"요약 생성 중 오류 발생: {e}"

    return summaries


# ─────────────────────────────────────────────
# 3. HTML 이메일 본문 생성
# ─────────────────────────────────────────────
def build_email_html(news_data: dict, summaries: dict) -> str:
    """뉴스 + 요약을 보기 좋은 HTML 이메일로 만듭니다."""
    today = datetime.now().strftime("%Y년 %m월 %d일 (%a)")

    # 카테고리 섹션 생성
    sections_html = ""
    category_colors = {
        "AI/테크 트렌드": "#0066FF",
        "주식/시장 동향": "#00AA66",
    }

    for category, articles in news_data.items():
        color = category_colors.get(category, "#333333")
        summary = summaries.get(category, "")

        # 기사 링크 목록
        articles_html = "".join([
            f'<li style="margin:6px 0;"><a href="{a["link"]}" style="color:#444;text-decoration:none;font-size:13px;">→ {a["title"]}</a></li>'
            for a in articles
        ])

        sections_html += f"""
        <div style="margin-bottom:36px;">
            <h2 style="font-size:16px;font-weight:700;color:{color};
                       border-left:4px solid {color};padding-left:12px;margin-bottom:12px;">
                {category}
            </h2>

            <!-- AI 요약 박스 -->
            <div style="background:#f7f9fc;border-radius:8px;padding:16px;
                        margin-bottom:14px;font-size:13.5px;color:#333;line-height:1.7;
                        white-space:pre-wrap;">
{summary}
            </div>

            <!-- 원문 링크 -->
            <details style="cursor:pointer;">
                <summary style="font-size:12px;color:#888;margin-bottom:6px;">
                    📎 원문 기사 보기 ({len(articles)}건)
                </summary>
                <ul style="padding-left:16px;margin:8px 0;">
                    {articles_html}
                </ul>
            </details>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family:'Apple SD Gothic Neo',Arial,sans-serif;
                 max-width:620px;margin:0 auto;padding:24px;color:#222;">

        <!-- 헤더 -->
        <div style="border-bottom:2px solid #0066FF;padding-bottom:16px;margin-bottom:28px;">
            <p style="font-size:12px;color:#888;margin:0 0 4px;">MORNING DIGEST</p>
            <h1 style="font-size:22px;font-weight:800;margin:0 0 4px;">
                📰 오늘의 AI·시장 브리핑
            </h1>
            <p style="font-size:13px;color:#666;margin:0;">{today}</p>
        </div>

        <!-- 본문 섹션들 -->
        {sections_html}

        <!-- 푸터 -->
        <div style="border-top:1px solid #eee;padding-top:16px;margin-top:8px;">
            <p style="font-size:11px;color:#aaa;margin:0;">
                🤖 이 메일은 Python + Claude API로 자동 생성되었습니다.<br>
                github.com/YOUR_ID/morning-news-digest
            </p>
        </div>

    </body>
    </html>
    """
    return html


# ─────────────────────────────────────────────
# 4. 이메일 발송
# ─────────────────────────────────────────────
def send_email(html_body: str):
    """Gmail SMTP로 HTML 이메일을 발송합니다."""
    today = datetime.now().strftime("%m/%d")
    subject = f"[Daily Digest] AI·시장 브리핑 {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PW)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"✅ 이메일 발송 완료 → {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 뉴스 수집 시작...")
    news_data = fetch_news(RSS_FEEDS, MAX_ARTICLES_PER_CATEGORY)

    total = sum(len(v) for v in news_data.values())
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 총 {total}개 기사 수집 완료")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Claude로 요약 중...")
    summaries = summarize_with_claude(news_data)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 이메일 생성 및 발송 중...")
    html_body = build_email_html(news_data, summaries)
    send_email(html_body)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 완료! 🎉")


if __name__ == "__main__":
    main()
