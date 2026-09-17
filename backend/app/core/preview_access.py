"""Optional server-side preview gate, covering UI, assets, docs and every API."""
import hashlib
import hmac
import secrets
import time
from urllib.parse import parse_qs, urlsplit
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.core.config import settings

COOKIE = 'miraati_preview_session'
TTL = 7 * 24 * 3600


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 210000).hex()
    return f'{salt}:{digest}'


def password_valid(candidate):
    try:
        salt, expected = settings.PREVIEW_PASSWORD_HASH.split(':', 1)
        return hmac.compare_digest(password_hash(candidate, salt).split(':', 1)[1], expected)
    except ValueError:
        return False


def session_token():
    payload = f'{int(time.time())}.{secrets.token_hex(16)}'
    signature = hmac.new(settings.PREVIEW_SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f'{payload}.{signature}'


def session_valid(token):
    try:
        timestamp, nonce, signature = token.split('.')
        age = time.time() - int(timestamp)
        expected = hmac.new(settings.PREVIEW_SESSION_SECRET.encode(), f'{timestamp}.{nonce}'.encode(), hashlib.sha256).hexdigest()
        return 0 <= age <= TTL and hmac.compare_digest(signature, expected)
    except (ValueError, AttributeError):
        return False


def login_page(error=False):
    message = '<p role="alert">Password not accepted · كلمة المرور غير صحيحة</p>' if error else ''
    return HTMLResponse('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Miraati · Private preview</title><style>body{margin:0;background:#f8f5ef;color:#34424b;font:18px system-ui;display:grid;min-height:100vh;place-items:center}main{max-width:420px;margin:24px;padding:32px;border:1px solid #ded6c8;border-radius:24px;background:white}input,button{box-sizing:border-box;width:100%;padding:14px;margin-top:14px;border:1px solid #baa16d;border-radius:20px;font:inherit}button{background:#34424b;color:white}p{line-height:1.6}</style></head><body><main><h1>Private preview</h1><h2 lang="ar" dir="rtl">معاينة خاصة — مرآتي</h2><p>For invited testers only.<br><span lang="ar">للمشاركين المدعوين فقط.</span></p>''' + message + '''<form method="post" action="/preview/login"><label for="password">Password · كلمة المرور</label><input id="password" name="password" type="password" autocomplete="current-password" required maxlength="256"><button type="submit">Enter · دخول</button></form></main></body></html>''', status_code=401 if error else 200)


class PreviewAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not settings.PREVIEW_PASSWORD_HASH or len(settings.PREVIEW_SESSION_SECRET) < 32:
            return JSONResponse({'detail': 'Preview access is not configured'}, status_code=503)
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('origin')
            if origin and urlsplit(origin).netloc != request.headers.get('host'):
                return JSONResponse({'detail': 'Cross-origin write rejected'}, status_code=403)
        if request.url.path == '/preview/login' and request.method == 'GET':
            response = login_page()
        elif request.url.path == '/preview/login' and request.method == 'POST':
            body = await request.body()
            password = parse_qs(body.decode(errors='replace')).get('password', [''])[0] if len(body) < 2048 else ''
            if password_valid(password):
                response = RedirectResponse('/', status_code=303)
                response.set_cookie(COOKIE, session_token(), max_age=TTL, httponly=True,
                                    secure=settings.ENVIRONMENT != 'local', samesite='strict', path='/')
            else:
                response = login_page(error=True)
        elif not session_valid(request.cookies.get(COOKIE)):
            response = JSONResponse({'detail': 'Private preview login required'}, status_code=401) if request.url.path.startswith('/api/') else RedirectResponse('/preview/login', status_code=303)
        elif request.url.path == '/preview/logout' and request.method == 'POST':
            response = RedirectResponse('/preview/login', status_code=303)
            response.delete_cookie(COOKIE, path='/')
        else:
            response = await call_next(request)
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
        response.headers['Cache-Control'] = 'no-store'
        # Preserve the Origin on same-site HTML form POSTs (login/logout).
        # no-referrer turns it into null in browsers and trips the CSRF check.
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
