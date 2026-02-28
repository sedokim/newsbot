import feedparser
from newspaper import Article
from googlenewsdecoder import gnewsdecoder
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import os
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = "sedokim123@gmail.com"
# ----------------

def get_news_content(keyword):
    rss_url = f"https://news.google.com/rss/search?q={keyword}+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_body = f"<h2>🔍 '{keyword}' 관련 주요 뉴스 리포트</h2><br>"
    print(f"🚀 '{keyword}' 뉴스 수집 및 이메일 준비 중...")

    for entry in feed.entries[:3]:
        encoded_url = entry.link
        try:
            decoded_res = gnewsdecoder(encoded_url)
            real_url = decoded_res.get('decoded_url') if decoded_res.get('status') else encoded_url
            
            article = Article(real_url, language='ko')
            article.download()
            article.parse()
            
            title = article.title
            content = article.text.strip()[:300] + "..." if article.text else "본문을 가져올 수 없습니다."
            
            # 이메일에 담을 HTML 내용 구성
            news_body += f"<h3>📌 {title}</h3>"
            news_body += f"<p>🔗 <a href='{real_url}'>원문 링크 보기</a></p>"
            news_body += f"<p>📝 요약내용:<br>{content}</p>"
            news_body += "<hr>"
            
            time.sleep(1) 
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            continue
    
    return news_body

def send_email(content):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"📅 오늘의 뉴스 브리핑 ({time.strftime('%Y-%m-%d')})"
        
        # HTML 형식으로 본문 추가
        msg.attach(MIMEText(content, 'html'))
        
        # SMTP 서버 연결 (Gmail 기준)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ 이메일 발송 성공!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

def job():
    keyword = "인공지능" # 여기에 원하는 키워드 고정
    news_html = get_news_content(keyword)

    send_email(news_html)
if __name__ == "__main__":
    job()
