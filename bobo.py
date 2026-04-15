import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 🔑 Telegram
BOT_TOKEN = "8728734920:AAHnOupiBs2EWLqHrftSYm4ExZaZNa2s6Yc"
CHAT_ID = "777274337"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Store matches dynamically
MATCHES = []

last_data = {}

def send(msg):
    requests.post(f"{BASE_URL}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# 🔥 Get Telegram messages
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    res = requests.get(url, params=params)
    return res.json()

# 🎯 Handle commands
def handle_message(text):
    global MATCHES

    if text.startswith("/add"):
        try:
            url = text.split(" ")[1]

            match = {
                "name": url.split("/")[-1],
                "url": url
            }

            MATCHES.append(match)
            send(f"✅ Added match: {match['name']}")

        except:
            send("❌ Use: /add <link>")

    elif text.startswith("/list"):
        if not MATCHES:
            send("📭 No matches added")
        else:
            msg = "📋 Active Matches:\n"
            for m in MATCHES:
                msg += f"- {m['name']}\n"
            send(msg)

    elif text.startswith("/remove"):
        name = text.replace("/remove ", "")
        MATCHES = [m for m in MATCHES if m["name"] != name]
        send(f"❌ Removed: {name}")

# ⚙️ Chrome setup
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

print("🚀 Dynamic Bot Started...")

last_update_id = None

while True:
    try:
        # 📩 Read Telegram messages
        updates = get_updates(last_update_id)

        for u in updates["result"]:
            last_update_id = u["update_id"] + 1

            if "message" in u:
                text = u["message"].get("text", "")
                handle_message(text)

        # 🔍 Process matches
        for match in MATCHES:
            driver.get(match["url"])
            time.sleep(6)

            elements = driver.find_elements(By.XPATH, "//div")

            values = []
            for e in elements:
                txt = e.text.strip()
                if txt.isdigit():
                    num = int(txt)
                    if 5 <= num <= 120:
                        values.append(num)

            values = list(dict.fromkeys(values))

            if len(values) < 2:
                continue

            team1 = values[0]
            team2 = values[1]

            # Fav logic
            if team1 < team2:
                fav = "Team1"
                back = team1
                lay = team2
            else:
                fav = "Team2"
                back = team2
                lay = team1

            key = match["name"]

            # ENTRY
            if key not in last_data or last_data[key] != (back, lay):

                msg = f"""📢 MATCH ALERT

🏏 {key}
📢 Fav: {fav}

💙 Back: {back}
💗 Lay: {lay}
"""
                send(msg)

                if lay <= 5:
                    send("🔥 EXTREME ENTRY")
                elif lay <= 10:
                    send("🚨 HIGH ENTRY")
                elif lay <= 20:
                    send("⚡ STRONG ENTRY")
                elif lay <= 30:
                    send("📢 ENTRY ZONE")

            # SHARP MOVE
            if key in last_data:
                old_back, old_lay = last_data[key]
                if abs(lay - old_lay) >= 5:
                    send(f"⚡ SHARP MOVE\n{old_lay} → {lay}")

            last_data[key] = (back, lay)

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
