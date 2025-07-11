import requests
import json
import websocket
import threading

class NeoAPI:
    def __init__(self, consumer_key, consumer_secret, environment="prod", access_token=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment
        self.access_token = access_token
        self.base_url = "https://gw-napi.kotaksecurities.com" if environment == "prod" else "https://uat-gw-napi.kotaksecurities.com"
        self.session = requests.Session()
        self._ws = None
        self._callbacks = {}

    def login(self, mobilenumber, password):
        url = f"{self.base_url}/login/1.0/login/v6/login"
        payload = {
            "mobileNumber": mobilenumber,
            "password": password,
            "source": "WEB"
        }
        return self.session.post(url, json=payload).json()

    def session_2fa(self, OTP):
        url = f"{self.base_url}/login/1.0/login/v6/validateotp"
        payload = {"otp": OTP, "source": "WEB"}
        response = self.session.post(url, json=payload)
        data = response.json()
        if "data" in data and "access_token" in data["data"]:
            self.access_token = data["data"]["access_token"]
        return data

    def get_headers(self):
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def quotes(self, instrument_tokens, session_token, sid, server_id, isIndex=False, quote_type=""):
        url = f"{self.base_url}/feed/1.0/quotes"
        payload = {
            "instrument_tokens": instrument_tokens,
            "session_token": session_token,
            "sid": sid,
            "server_id": server_id,
            "isIndex": isIndex,
            "quote_type": quote_type
        }
        return self.session.post(url, headers=self.get_headers(), json=payload).json()

    # ✅ Patched: Set callback for WebSocket messages
    def set_callback(self, event_type, callback):
        self._callbacks[event_type] = callback

    # ✅ Patched: Connect to WebSocket and handle events
    def connect_ws(self, session_token, sid, server_id):
        ws_url = f"wss://api.kotaksecurities.com/feed/v1?sid={sid}&token={session_token}&server_id={server_id}"
        
        def on_message(ws, message):
            if "quote" in self._callbacks:
                self._callbacks["quote"](json.loads(message))

        def on_error(ws, error):
            if "error" in self._callbacks:
                self._callbacks["error"](error)

        def on_close(ws):
            if "close" in self._callbacks:
                self._callbacks["close"]()

        def on_open(ws):
            if "open" in self._callbacks:
                self._callbacks["open"]()
        
        self._ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        thread = threading.Thread(target=self._ws.run_forever)
        thread.daemon = True
        thread.start()

    # ✅ Patched: Subscribe to instruments
    def subscribe(self, instruments, action="subscribe"):
        if not self._ws:
            raise Exception("WebSocket is not connected.")
        payload = {
            "action": action,
            "params": instruments
        }
        self._ws.send(json.dumps(payload))
