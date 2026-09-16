"""Upload this isolated preview's server environment without printing credentials."""
import json
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'temp/preview-secrets.json').read_text())
assert config['PREVIEW_MODE']=='true' and '/miraati_preview?' in config['DATABASE_URL']
for key,value in config.items():
    result=subprocess.run(['vercel','env','add',key,'preview','--force','--yes','--sensitive','--project','miraati-private-preview'],input=value,text=True,capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Failed to configure {key}; inspect Vercel project environment settings')
    print(f'Configured {key}',flush=True)
