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
# Dummy Web Server (Render Free 유지용)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_server():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_server, daemon=True).start()

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
    return "OUT OF STOCK" not in soup.get_text().upper()

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
