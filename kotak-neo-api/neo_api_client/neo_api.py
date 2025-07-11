class NeoAPI:
    def __init__(self, consumer_key, consumer_secret, environment="prod"):
        # your logic here
        pass
# --- PATCHED METHODS ---

def set_callback(self, event_type, callback):
    if not hasattr(self, "_callbacks"):
        self._callbacks = {}
    self._callbacks[event_type] = callback

def subscribe(self, instruments, action="subscribe"):
    if not hasattr(self, "_ws") or self._ws is None:
        raise Exception("WebSocket not connected")
    payload = {
        "action": action,
        "params": instruments
    }
    self._ws.send(json.dumps(payload))
