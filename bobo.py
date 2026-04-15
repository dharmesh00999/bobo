import time
import requests
from bs4 import BeautifulSoup
import os

# =============================
# 🔑 TELEGRAM CONFIG FROM RENDER
# =============================
BOT_TOKEN = os.getenv("8728734920:AAHnOupiBs2EWLqHrftSYm4ExZaZNa2s6Yc")
CHAT_ID = os.getenv("777274337")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        requests.post(url, data=data)
    except:
        pass

# =============================
# 📊 MATCH CONFIG
# =============================
MATCHES = [
    {
        "name": "RCB vs LSG",
        "url": "https://crex.com/cricket-live-score/lsg-vs-rcb-23rd-match-indian-premier-league-2026-match-updates-1184"
    }
]

last_data = {}

# =============================
# 🧠 FETCH ODDS
# =============================
def get_odds(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        values = []

        for div in soup.find_all("div"):
            txt = div.text.strip()

            if txt.isdigit():
                num = int(txt)
                if 1 <= num <= 120:
                    values.append(num)

        values = list(dict.fromkeys(values))

        if len(values) >= 2:
            return values[0], values[1]

    except Exception as e:
        print("Error:", e)

    return None, None

# =============================
# ⚙️ LOGIC
# =============================
def check_matches():
    global last_data

    for match in MATCHES:
        name = match["name"]
        url = match["url"]

        back, lay = get_odds(url)

        if not back or not lay:
            print("Waiting for data...")
            continue

        fav = name.split(" vs ")[0] if back < lay else name.split(" vs ")[1]

        print(f"{name} → Back:{back} Lay:{lay}")

        # ENTRY ALERT
        if lay <= 30:
            if last_data.get(name) != f"entry_{lay}":
                msg = f"🔥 ENTRY ALERT\nFav: {fav}\nBack: {back}\nLay: {lay}"
                send_telegram(msg)
                last_data[name] = f"entry_{lay}"

        # RATE CHANGE ALERT
        prev = last_data.get(f"{name}_last")

        if prev:
            if abs(lay - prev) >= 10:
                msg = f"⚡ RATE JUMP\n{fav}\nOld: {prev} → New: {lay}"
                send_telegram(msg)

        last_data[f"{name}_last"] = lay

# =============================
# 🔁 LOOP
# =============================
print("🚀 CREX CLOUD BOT STARTED...")

while True:
    check_matches()
    time.sleep(10)
