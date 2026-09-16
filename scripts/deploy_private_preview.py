"""Deploy only the isolated private preview; explicit staging avoids first-deploy promotion."""
import base64
import json
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bundle=root/'temp/mothers-preview-deploy'
files=[]
for file in sorted(bundle.rglob('*')):
    relative=file.relative_to(bundle)
    if not file.is_file() or '.vercel' in relative.parts or '__pycache__' in relative.parts:
        continue
    if file.name.startswith('.env'):
        raise RuntimeError('Environment files must not be uploaded')
    files.append({'file':str(relative),'data':base64.b64encode(file.read_bytes()).decode(),'encoding':'base64'})
payload={'name':'miraati-private-preview','project':'prj_Ntdhk8Jt76Pz4ZtwVZMCO4AcdYJH','target':'staging','files':files,'projectSettings':{'framework':None,'serverlessFunctionRegion':'fra1'}}
request=root/'temp/preview-deployment-request.json';request.write_text(json.dumps(payload))
print('Uploading',len(files),'files to isolated staging target',flush=True)
result=subprocess.run(['vercel','api','/v13/deployments','-X','POST','--input',str(request),'-H','Content-Type: application/json','--raw'],capture_output=True,text=True)
if result.returncode:
    print(result.stderr);raise SystemExit(result.returncode)
response=json.loads(result.stdout)
(root/'temp/preview-deployment.json').write_text(json.dumps(response))
if response.get('target')=='production':
    subprocess.run(['vercel','api',f'/v12/deployments/{response["id"]}/cancel','-X','PATCH','--silent'],check=True)
    raise RuntimeError('Unexpected production target; build cancelled')
print(response['id'],response.get('target'),'https://'+response['url'])
