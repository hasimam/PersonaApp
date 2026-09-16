"""Assemble a secret-free, isolated Vercel deployment; never deploys by itself."""
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / 'temp/mothers-preview-deploy'
target.mkdir(parents=True, exist_ok=True)
# CRA's production .env points to Fly. Explicitly override it for this build.
import os
env = dict(os.environ, REACT_APP_API_URL='', REACT_APP_PRIVATE_PREVIEW='true', GENERATE_SOURCEMAP='false')
subprocess.run(['npm', 'run', 'build'], cwd=root / 'frontend', env=env, check=True)
shutil.copytree(root / 'backend/app', target / 'app', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
if (target / 'site').exists():
    shutil.rmtree(target / 'site')
shutil.copytree(root / 'frontend/build', target / 'site')
shutil.copy(root / 'backend/requirements.txt', target / 'requirements.txt')
(target / 'api').mkdir(exist_ok=True)
(target / 'api/index.py').write_text('''from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.main import app
from app.core.config import settings

if not settings.PREVIEW_MODE:
    raise RuntimeError("This deployment must have PREVIEW_MODE=true")

site = Path(__file__).resolve().parents[1] / "site"
# Override the existing API root health handler only for the private UI bundle.
app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/"]
@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    if path.startswith(("api/", "docs", "openapi", "redoc")):
        raise HTTPException(404)
    candidate = (site / path).resolve()
    if not candidate.is_relative_to(site):
        raise HTTPException(404)
    if candidate.is_file():
        return FileResponse(candidate)
    if path and "." in path.rsplit("/", 1)[-1]:
        raise HTTPException(404)
    return FileResponse(site / "index.html")
''')
(target / 'vercel.json').write_text(json.dumps({
    'version': 2,
    'builds': [{'src': 'api/index.py', 'use': '@vercel/python', 'config': {'includeFiles': ['app/**', 'site/**']}}],
    'routes': [{'src': '/(.*)', 'dest': '/api/index.py'}]
}, indent=2)+'\n')
(target / '.python-version').write_text('3.12\n')
print(f'Isolated deployment bundle: {target}')
