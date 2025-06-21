from fastapi import FastAPI, Request
import requests, asyncio, websockets, json
from datetime import datetime, timedelta
import csv, io
import threading

app = FastAPI()

ACCESS_TOKEN = "eyJ4NXQiOiJNbUprWWpVMlpETmpNelpqTURBM05UZ3pObUUxTm1NNU1qTXpNR1kyWm1OaFpHUTFNakE1TmciLCJraWQiOiJaalJqTUdRek9URmhPV1EwTm1WallXWTNZemRtWkdOa1pUUmpaVEUxTlRnMFkyWTBZVEUyTlRCaVlURTRNak5tWkRVeE5qZ3pPVGM0TWpGbFkyWXpOUV9SUzI1NiIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJjbGllbnQ3MzQyOSIsImF1dCI6IkFQUExJQ0FUSU9OIiwiYXVkIjoiVF9VcmsxWUZjZ21qY3lZZUprano4SnR5TElvYSIsIm5iZiI6MTc1MDQ0MTQzNiwiYXpwIjoiVF9VcmsxWUZjZ21qY3lZZUprano4SnR5TElvYSIsInNjb3BlIjoiZGVmYXVsdCIsImlzcyI6Imh0dHBzOlwvXC9uYXBpLmtvdGFrc2VjdXJpdGllcy5jb206NDQzXC9vYXV0aDJcL3Rva2VuIiwiZXhwIjoxNzUwNTI3ODM2LCJpYXQiOjE3NTA0NDE0MzYsImp0aSI6ImVjYjAwNDEyLTIxYWItNDE1OC1hNzhkLTgyODhlN2ExMzhkZCJ9.Ke9bpJsAbtIEDjxcVZFKMMBNor0jopEQ4h8hmpBkjG7oEVNyGVZ2KvEQdMa6A2ChXXaW-WYucddbbjOIhN1wY2erTPZXlPlG_uYYSJ9EwkzbDONPx2lbuQCdrReWNMmbPM7SMr2qPM2ORpWiNXA-E88z3nu5chhCVIczcl-13NClJGnIMcg8uCVvXkRKocEOROKL9tKhtmOOUwmKW-HBvhHeYv7TLZWWzcbQrtP-tzaPuqM1RNSgiGl6b_XZT7TbLJ4FRJO33dOd0ZxatfOhmoW83_XQb97LPKYGkoz-GoMiB1IrYNKMDe5COB1yBQaQXb81A0GwDMKWdy5RXQOX6g"  

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "accept": "application/json"
}

KOTAK_ORDER_URL = "https://gw-napi.kotaksecurities.com/Orders/2.0/ordermgmt/placeorder"
MASTER_FILE_PATH_URL = "https://gw-napi.kotaksecurities.com/masterscrip/v4/file-paths"

# Shared variable to store live Nifty price
latest_nifty_price = {"ltp": 0}


# 🔁 Background WebSocket task
async def kotak_ws_client():
    uri = "ws://gw-napi.kotaksecurities.com:9099/realtime/1.0"
    try:
        async with websockets.connect(uri, extra_headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }) as websocket:
            payload = {
                "msg_type": "subscribe",
                "instrument_tokens": ["nse_cm|999920000"],  # Nifty Index token
                "feed_type": "ltp"
            }
            await websocket.send(json.dumps(payload))
            print("✅ Subscribed to Nifty LTP WebSocket")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if isinstance(data, list) and "ltp" in data[0]:
                    ltp = float(data[0]["ltp"]) / 100
                    latest_nifty_price["ltp"] = ltp
                    print(f"📈 Updated Nifty LTP: ₹{ltp}")
    except Exception as e:
        import traceback
        print("❌ WebSocket error:", str(e))
        traceback.print_exc()

    

# Launch WebSocket in background thread
def start_ws_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(kotak_ws_client())


threading.Thread(target=start_ws_background, daemon=True).start()


def get_latest_nifty_price():
    return latest_nifty_price["ltp"]


def get_latest_nfo_option_scrip():
    try:
        res = requests.get(MASTER_FILE_PATH_URL, headers=HEADERS)
        data = res.json()
        for file in data.get("filePaths", []):
            if "NFO" in file.get("fileName", "") and file.get("fileType") == "option":
                return file["fileURL"]
    except Exception as e:
        print("❌ Error fetching scrip file:", str(e))
    return None


def fetch_matching_scrip(expiry_yyyymmdd, strike, option_type):
    file_url = get_latest_nfo_option_scrip()
    if not file_url:
        return None, None

    try:
        res = requests.get(file_url)
        content = res.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            if (
                row.get("Symbol") == "NIFTY" and
                row.get("OptionType") == option_type and
                row.get("StrikePrice") == str(strike) and
                row.get("ExpiryDate", "").replace("-", "").replace("/", "") == expiry_yyyymmdd
            ):
                print(f"✅ Found matching scrip: {row['TradingSymbol']}")
                return row["TradingSymbol"], row["InstrumentToken"]
    except Exception as e:
        print("❌ Error parsing scrip file:", str(e))

    return None, None


def get_next_expiry():
    today = datetime.now()
    days_until_thursday = (3 - today.weekday() + 7) % 7
    days_until_thursday = 7 if days_until_thursday == 0 else days_until_thursday
    expiry = today + timedelta(days=days_until_thursday)
    return expiry.strftime("%d%b").upper(), expiry.strftime("%Y%m%d")


def calculate_atm_strike(price):
    return int(round(price / 50.0) * 50)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    signal = data.get("signal")

    if signal not in ["BUY_CE", "SELL_CE", "BUY_PE", "SELL_PE"]:
        return {"status": "error", "message": "Invalid signal"}

    option_type = "CE" if "CE" in signal else "PE"
    transaction_type = "BUY" if "BUY" in signal else "SELL"

    nifty_price = get_latest_nifty_price()
    if nifty_price == 0:
        return {"status": "error", "message": "Nifty price unavailable (WebSocket not ready)"}

    strike = calculate_atm_strike(nifty_price)
    expiry_str, expiry_full = get_next_expiry()
    trading_symbol, instrument_token = fetch_matching_scrip(expiry_full, strike, option_type)

    if not trading_symbol:
        return {"status": "error", "message": "Matching option scrip not found."}

    payload = {
        "instrumentToken": instrument_token,
        "tradingSymbol": trading_symbol,
        "transactionType": transaction_type,
        "orderType": "MARKET",
        "quantity": 75,
        "price": 0.0,
        "validity": "DAY",
        "productType": "NRML",
        "exchange": "NFO",
        "orderSource": "API"
    }

    try:
        res = requests.post(KOTAK_ORDER_URL, headers=HEADERS, json=payload)
        result = res.json()
        print("✅ Order Placed:", result)
        return {"status": "order_sent", "response": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
