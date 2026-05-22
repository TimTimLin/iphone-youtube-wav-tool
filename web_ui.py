#!/usr/bin/env python3
import html
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8765


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond_page()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = urllib.parse.parse_qs(body)
        url = (form.get("url") or [""])[0].strip()
        if not url:
            self.respond_page(error="請貼上 YouTube 網址。")
            return

        script = Path(__file__).with_name("ytwav.py")
        try:
            result = subprocess.run(
                [sys.executable, str(script), url],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=1800,
            )
            output = result.stdout.strip()
            if result.returncode == 0:
                self.respond_page(success="轉換完成。", output=output)
            else:
                self.respond_page(error="轉換失敗。", output=output)
        except subprocess.TimeoutExpired:
            self.respond_page(error="轉換逾時，請改用較短音訊或稍後再試。")

    def respond_page(self, success=None, error=None, output=""):
        body = render_page(success=success, error=error, output=output)
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def render_page(success=None, error=None, output=""):
    success_html = f'<div class="notice ok">{html.escape(success)}</div>' if success else ""
    error_html = f'<div class="notice error">{html.escape(error)}</div>' if error else ""
    output_html = f"<pre>{html.escape(output)}</pre>" if output else ""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>YouTube WAV</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    body {{
      margin: 0;
      padding: 24px;
      background: Canvas;
      color: CanvasText;
    }}
    main {{
      max-width: 560px;
      margin: 0 auto;
    }}
    h1 {{
      font-size: 28px;
      margin: 0 0 20px;
    }}
    label {{
      display: block;
      font-size: 14px;
      margin-bottom: 8px;
    }}
    input {{
      width: 100%;
      box-sizing: border-box;
      font-size: 16px;
      padding: 14px;
      border: 1px solid #8a8a8a;
      border-radius: 8px;
      margin-bottom: 14px;
    }}
    button {{
      width: 100%;
      font-size: 17px;
      font-weight: 700;
      padding: 14px;
      border: 0;
      border-radius: 8px;
      background: #1677ff;
      color: white;
    }}
    .notice {{
      margin: 16px 0;
      padding: 12px;
      border-radius: 8px;
      font-weight: 600;
    }}
    .ok {{
      background: #d7f7df;
      color: #0d5721;
    }}
    .error {{
      background: #ffe1e1;
      color: #8a1111;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      padding: 12px;
      border-radius: 8px;
      background: rgba(127, 127, 127, .14);
      font-size: 13px;
    }}
    p {{
      line-height: 1.5;
      color: #666;
    }}
  </style>
</head>
<body>
  <main>
    <h1>YouTube 轉 WAV</h1>
    <form method="post">
      <label for="url">YouTube 網址</label>
      <input id="url" name="url" type="url" placeholder="https://www.youtube.com/watch?v=..." required>
      <button type="submit">轉成 WAV</button>
    </form>
    {success_html}
    {error_html}
    {output_html}
    <p>輸出位置：iSH 的 <code>~/Documents/YouTube WAV</code>。請只處理你有權下載與保存的內容。</p>
  </main>
</body>
</html>"""


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Open Safari: http://{HOST}:{PORT}")
    print("Keep iSH open while converting.")
    server.serve_forever()


if __name__ == "__main__":
    main()
