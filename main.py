import requests
import time
import os
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# --------------------
# Discord
# --------------------
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(msg):
    if not DISCORD_WEBHOOK_URL:
        return
    requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

# --------------------
# Dummy web server (Render Free 유지용)
# --------------------
app = Flask(__name__)

def run_server():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_server, daemon=True).start()

# --------------------
# Stock check functions
# --------------------
HEADERS = {"User-Agent": "Mozilla/5.0"}

def sm_stock(url):
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    return "품절" not in soup.get_text()

def allmd_stock(url):
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    return "SOLD OUT" not in soup.get_text().upper()

def ktown_stock(url):
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
    return "Out of stock" not in soup.get_text()

# --------------------
# Products
# --------------------
products = [
    ("SM", "https://smtownandstore.com/product/2025-nct-wish-1st-concert-tour-into-the-wish-our-wish-wish-book-set/27714/category/53/display/1/"),
    ("ALLMD", "https://allmd.com/product/%EC%97%94%EC%8B%9C%ED%8B%B0-%EC%9C%84%EC%8B%9C-nct-wish-concert-tour-into-the-wish-our-wish-md-%EC%9C%84%EC%8B%9C%EB%B6%81-set/11468/category/657/display/1/"),
    ("KTOWN4U", "https://kr.ktown4u.com/iteminfo?goods_no=149759"),
]

checkers = {
    "SM": sm_stock,
    "ALLMD": allmd_stock,
    "KTOWN4U": ktown_stock,
}

# --------------------
# Start
# --------------------
send_discord("🟢 재고 감시 시작 (정상 실행)")

state = {}

while True:
    for site, url in products:
        try:
            now = checkers[site](url)
            before = state.get(url, False)

            if now and not before:
                send_discord(f"🔥 재고 발생!\n[{site}]\n{url}")

            state[url] = now
        except Exception as e:
            send_discord(f"⚠️ 오류: {e}")

    time.sleep(300)
