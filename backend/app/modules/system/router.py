from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.settings.config import settings

router = APIRouter(tags=["System"])

_start_time = datetime.now(timezone.utc)


@router.get("/health", response_class=HTMLResponse)
async def health_check():
    uptime = datetime.now(timezone.utc) - _start_time
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    uptime_str = f"{h}h {m}m {s}s"
    return HTMLResponse(_info_html(uptime_str))


@router.get("/info", response_class=HTMLResponse)
async def system_info():
    uptime = datetime.now(timezone.utc) - _start_time
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    uptime_str = f"{h}h {m}m {s}s"
    return HTMLResponse(_info_html(uptime_str))


def _info_html(uptime: str) -> str:
    env = settings.ENVIRONMENT
    env_color = "#22c55e" if env == "production" else "#f59e0b"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WorkmateOS — System Info</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }}
    .card {{
      background: #1a1f2e;
      border: 1px solid #2d3748;
      border-radius: 16px;
      padding: 2.5rem 3rem;
      width: 100%;
      max-width: 520px;
      box-shadow: 0 25px 50px rgba(0,0,0,0.4);
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 2rem;
    }}
    .logo-icon {{
      width: 40px; height: 40px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
    }}
    .logo-text {{ font-size: 1.25rem; font-weight: 700; color: #f8fafc; }}
    .logo-sub {{ font-size: 0.75rem; color: #64748b; margin-top: 2px; }}
    .badge {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 4px 12px; border-radius: 999px;
      font-size: 0.75rem; font-weight: 600;
      background: #14532d; color: #86efac;
      border: 1px solid #166534;
      margin-bottom: 1.5rem;
    }}
    .dot {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.4 }} }}
    .section-label {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: .08em;
      text-transform: uppercase; color: #475569;
      margin: 1.5rem 0 0.75rem;
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    tr {{ border-bottom: 1px solid #1e293b; }}
    tr:last-child {{ border-bottom: none; }}
    td {{ padding: 10px 0; font-size: 0.875rem; }}
    td:first-child {{ color: #64748b; width: 45%; }}
    td:last-child {{ color: #f1f5f9; font-weight: 500; text-align: right; }}
    .env-badge {{
      display: inline-block; padding: 2px 8px; border-radius: 4px;
      font-size: 0.75rem; font-weight: 600;
      background: {env_color}22; color: {env_color};
    }}
    .mono {{ font-family: "SF Mono", "Fira Code", monospace; font-size: 0.8rem; }}
    .links {{ margin-top: 2rem; display: flex; gap: 10px; }}
    .link {{
      flex: 1; text-align: center; padding: 10px;
      border-radius: 8px; border: 1px solid #2d3748;
      color: #94a3b8; text-decoration: none; font-size: 0.8rem;
      transition: all .15s;
    }}
    .link:hover {{ background: #2d3748; color: #f1f5f9; border-color: #3b82f6; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <div>
        <div class="logo-text">WorkmateOS</div>
        <div class="logo-sub">K.I.T. Solutions — System Info</div>
      </div>
    </div>
    <div class="badge"><span class="dot"></span> Operational</div>

    <div class="section-label">Application</div>
    <table>
      <tr><td>Version</td><td class="mono">{settings.APP_VERSION}</td></tr>
      <tr><td>Environment</td><td><span class="env-badge">{env}</span></td></tr>
      <tr><td>Uptime</td><td class="mono">{uptime}</td></tr>
      <tr><td>Server Time</td><td class="mono">{now}</td></tr>
    </table>

    <div class="section-label">Links</div>
    <div class="links">
      <a class="link" href="/">Home</a>
      <a class="link" href="/docs">Swagger</a>
      <a class="link" href="/redoc">ReDoc</a>
    </div>
  </div>
</body>
</html>"""
