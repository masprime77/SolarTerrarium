import socket
import time
import config
from utils.config_loader import save as save_config

_HTML = (
    "<!DOCTYPE html>"
    "<html lang='en'>"
    "<head>"
    "<meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>SolarTerrarium</title>"
    "<style>"
    "*{box-sizing:border-box;margin:0;padding:0}"
    "body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
         "background:#111827;color:#e5e7eb;padding:16px;"
         "max-width:440px;margin:0 auto}"
    "h1{text-align:center;color:#fb923c;font-size:1.3rem;margin:12px 0 20px}"
    ".card{background:#1f2937;border-radius:12px;padding:16px;margin-bottom:14px}"
    "h2{font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;"
        "color:#6b7280;margin-bottom:14px}"
    ".f{margin-bottom:14px}"
    ".f:last-child{margin-bottom:0}"
    "label{display:block;font-size:.9rem;color:#d1d5db;margin-bottom:6px}"
    ".hint{font-size:.75rem;color:#6b7280;margin-top:4px}"
    "input[type=time],input[type=number]{"
        "width:100%;background:#111827;border:1px solid #374151;"
        "border-radius:8px;color:#f9fafb;padding:10px 12px;font-size:1rem}"
    "input[type=range]{width:100%;accent-color:#fb923c;margin-top:4px}"
    ".row{display:flex;align-items:center;gap:10px}"
    ".row input{flex:1}"
    ".val{min-width:44px;text-align:right;color:#fb923c;font-weight:600;"
          "font-size:.95rem}"
    "button{width:100%;background:#fb923c;color:#111827;border:none;"
            "border-radius:10px;padding:14px;font-size:1rem;"
            "font-weight:700;cursor:pointer;margin-top:4px}"
    "button:active{background:#ea7c1e}"
    ".msg{text-align:center;padding:10px 14px;border-radius:8px;"
          "margin-bottom:14px;font-size:.9rem}"
    ".ok{background:#052e16;color:#4ade80;border:1px solid #166534}"
    ".err{background:#450a0a;color:#f87171;border:1px solid #7f1d1d}"
    "footer{text-align:center;color:#4b5563;font-size:.75rem;margin-top:16px}"
    "</style>"
    "</head>"
    "<body>"
    "<h1>&#x1F33F; SolarTerrarium</h1>"
    "__MESSAGE__"
    "<form method='POST'>"

    "<div class='card'>"
    "<h2>&#x1F634; Sleep schedule</h2>"
    "<div class='f'>"
    "<label>Lights off at</label>"
    "<input type='time' name='sleep_start' value='__SLEEP_START__'>"
    "</div>"
    "<div class='f'>"
    "<label>Lights back on at</label>"
    "<input type='time' name='sleep_end' value='__SLEEP_END__'>"
    "</div>"
    "</div>"

    "<div class='card'>"
    "<h2>&#x1F4A1; Brightness</h2>"
    "<div class='f'>"
    "<label>Sun / Moon sphere</label>"
    "<div class='row'>"
    "<input type='range' name='brightness_ring' min='1' max='100' value='__BR_RING__'"
    " oninput='this.nextElementSibling.textContent=this.value+\"%\"'>"
    "<span class='val'>__BR_RING__%</span>"
    "</div>"
    "</div>"
    "<div class='f'>"
    "<label>Sky overhead strip</label>"
    "<div class='row'>"
    "<input type='range' name='brightness_overhead' min='1' max='100' value='__BR_OVER__'"
    " oninput='this.nextElementSibling.textContent=this.value+\"%\"'>"
    "<span class='val'>__BR_OVER__%</span>"
    "</div>"
    "</div>"
    "</div>"

    "<div class='card'>"
    "<h2>&#x1F4CD; Location</h2>"
    "<div class='f'>"
    "<label>Latitude</label>"
    "<input type='number' name='latitude' step='0.0001' value='__LAT__'>"
    "</div>"
    "<div class='f'>"
    "<label>Longitude</label>"
    "<input type='number' name='longitude' step='0.0001' value='__LON__'>"
    "<p class='hint'>Find yours: Google Maps &#8594; long-press your location</p>"
    "</div>"
    "</div>"

    "<button type='submit'>&#x1F4BE; Save &amp; Apply</button>"
    "</form>"
    "<footer>__HOSTNAME__</footer>"
    "</body>"
    "</html>"
)

_MSG_OK = (
    "<div class='msg ok'>&#10003; Saved &#8212; restarting in "
    "<span id='t'>3</span>s&hellip;"
    "<script>let n=3,el=document.getElementById('t');"
    "setInterval(()=>{n>0&&(el.textContent=--n)},1000)"
    "</script></div>"
)

_MSG_ERR = "<div class='msg err'>&#9888; Could not save settings. Try again.</div>"


class WebConfig:
    def __init__(self, port=80):
        self._restart_at = None
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("0.0.0.0", port))
        self._sock.listen(1)
        self._sock.setblocking(False)
        print("WebConfig listening on :{}", port)

    def poll(self):
        if self._restart_at is not None:
            if time.ticks_diff(time.ticks_ms(), self._restart_at) >= 0:
                import machine
                machine.reset()
            return

        try:
            conn, _ = self._sock.accept()
        except OSError:
            return

        try:
            conn.settimeout(5)
            method, body = self._read_request(conn)
            if method == "POST":
                ok = self._handle_post(body)
                self._send_page(conn, "ok" if ok else "err")
            else:
                self._send_page(conn, "")
        except Exception as e:
            print("WebConfig error:", e)
        finally:
            try:
                conn.close()
            except:
                pass

    def _read_request(self, conn):
        raw = b""
        while b"\r\n\r\n" not in raw:
            chunk = conn.recv(512)
            if not chunk:
                break
            raw += chunk

        header_raw, _, body_raw = raw.partition(b"\r\n\r\n")
        headers = header_raw.decode()

        content_length = 0
        for line in headers.split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":", 1)[1].strip())
                break

        while len(body_raw) < content_length:
            chunk = conn.recv(512)
            if not chunk:
                break
            body_raw += chunk

        method = headers.split("\r\n")[0].split(" ")[0]
        return method, body_raw.decode()

    def _handle_post(self, body):
        try:
            fields = _parse_form(body)

            ss = fields.get("sleep_start", "23:30")
            se = fields.get("sleep_end", "07:30")
            sh, sm = int(ss[:2]), int(ss[3:])
            eh, em = int(se[:2]), int(se[3:])

            data = {
                "sleep_start": [sh, sm],
                "sleep_end":   [eh, em],
                "brightness_ring":     round(int(fields.get("brightness_ring", 25)) / 100, 3),
                "brightness_overhead": round(int(fields.get("brightness_overhead", 25)) / 100, 3),
                "latitude":  float(fields.get("latitude",  config.LATITUDE)),
                "longitude": float(fields.get("longitude", config.LONGITUDE)),
            }

            save_config(data)
            self._restart_at = time.ticks_add(time.ticks_ms(), 3000)
            return True
        except Exception as e:
            print("WebConfig save error:", e)
            return False

    def _send_page(self, conn, msg_type):
        if msg_type == "ok":
            message = _MSG_OK
        elif msg_type == "err":
            message = _MSG_ERR
        else:
            message = ""

        br_ring = max(1, round(config.BRIGHTNESS_LED_RING * 100))
        br_over = max(1, round(config.BRIGHTNESS_OVERHEAD_LED * 100))
        ss = "{:02d}:{:02d}".format(config.SLEEP_START[0], config.SLEEP_START[1])
        se = "{:02d}:{:02d}".format(config.SLEEP_END[0], config.SLEEP_END[1])

        body = (
            _HTML
            .replace("__MESSAGE__",    message)
            .replace("__SLEEP_START__", ss)
            .replace("__SLEEP_END__",   se)
            .replace("__BR_RING__",     str(br_ring))
            .replace("__BR_OVER__",     str(br_over))
            .replace("__LAT__",         str(config.LATITUDE))
            .replace("__LON__",         str(config.LONGITUDE))
            .replace("__HOSTNAME__",    config.HOSTNAME)
        )

        body_bytes = body.encode("utf-8")
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(len(body_bytes))

        conn.send(header.encode())
        conn.send(body_bytes)


def _urldecode(s):
    res = []
    i = 0
    while i < len(s):
        if s[i] == "%" and i + 2 < len(s):
            res.append(chr(int(s[i+1:i+3], 16)))
            i += 3
        elif s[i] == "+":
            res.append(" ")
            i += 1
        else:
            res.append(s[i])
            i += 1
    return "".join(res)


def _parse_form(body):
    result = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[_urldecode(k)] = _urldecode(v)
    return result
