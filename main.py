import requests
import time
import os
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# =========================
# Slack Webhook
# =========================
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def send_slack(message):
    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL 없음")
        return
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=10
        )
    except Exception as e:
        print("❌ Slack 전송 오류:", e)

# =========================
# Stock Check Functions
# =========================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Stock Watcher Bot)"
}

def sm_stock(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    return "품절" not in soup.get_text()

def allmd_stock(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text().upper()
    return "SOLD OUT" not in text and "품절" not in text

def ktown_stock(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # 구매 버튼 찾기
    buy_btn = soup.select_one("button.btn_buy")

    if not buy_btn:
        return False

    # 버튼이 비활성화되어 있으면 품절
    if "disabled" in buy_btn.attrs:
        return False

    return True


# =========================
# Products
# =========================
products = [
    (
        "SMTOWN & STORE",
        "https://smtownandstore.com/product/2025-nct-wish-1st-concert-tour-into-the-wish-our-wish-wish-book-set/27714/category/53/display/1/"
    ),
    (
        "ALLMD",
        "https://allmd.com/product/%EC%97%94%EC%8B%9C%ED%8B%B0-%EC%9C%84%EC%8B%9C-nct-wish-concert-tour-into-the-wish-our-wish-md-%EC%9C%84%EC%8B%9C%EB%B6%81-set/11468/category/657/display/1/"
    ),
    (
        "KTOWN4U",
        "https://kr.ktown4u.com/iteminfo?goods_no=149759"
    ),
]

checkers = {
    "SMTOWN & STORE": sm_stock,
    "ALLMD": allmd_stock,
    "KTOWN4U": ktown_stock,
}

# =========================
# Background Watcher
# =========================
def stock_watcher():
    send_slack("🟢 재고 감시 시작 (슬랙 정상 실행)")
    last_state = {}

    while True:
        for name, url in products:
            try:
                in_stock = checkers[name](url)
                was_in_stock = last_state.get(url, False)

                if in_stock and not was_in_stock:
                    send_slack(
                        f"🔥 재고 발생!\n[{name}]\n{url}"
                    )

                last_state[url] = in_stock

            except Exception as e:
                send_slack(f"⚠️ 오류 발생 ({name})\n{e}")

        time.sleep(300)  # 5분마다 체크

# =========================
# Flask App (Render용 메인 프로세스)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

if __name__ == "__main__":
    Thread(target=stock_watcher, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
