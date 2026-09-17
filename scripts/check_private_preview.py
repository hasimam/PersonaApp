"""HTTP smoke check with synthetic journeys, using the local preview-access file."""
import http.cookiejar
import json
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

base=sys.argv[1].rstrip('/')
password=Path(sys.argv[2]).read_text().split('Password: ',1)[1].splitlines()[0]
jar=http.cookiejar.CookieJar()
client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def call(path, payload=None, method='GET', owner=None, raw=None, origin=None):
    headers={'Content-Type':'application/json', 'Origin':base}
    if owner: headers['X-Mother-Owner-Token']=owner
    if origin: headers['Origin']=origin
    data=json.dumps(payload).encode() if payload is not None else None
    if raw is not None:
        headers['Content-Type']='application/x-www-form-urlencoded';data=raw.encode()
    request=urllib.request.Request(base+path,data=data,headers=headers,method=method)
    try: response=client.open(request,timeout=45)
    except urllib.error.HTTPError as e: response=e
    body=response.read().decode()
    return response.status,body,response.headers

status,body,headers=call('/api/v1/mothers-mirror/journeys',{},'POST')
assert status==401,(status,body[:150])
status,body,headers=call('/mothers-mirror')
assert 'Private preview' in body and 'password' in body
assert 'noindex' in headers.get('X-Robots-Tag','')
assert headers.get('Referrer-Policy') == 'same-origin'
assert call('/preview/login',method='POST',raw='password=incorrect',origin='null')[0]==403
assert call('/preview/login',method='POST',raw='password=incorrect')[0]==401
assert call('/preview/login',method='POST',raw=urllib.parse.urlencode({'password':password}),origin='https://untrusted.example')[0]==403
status,body,_=call('/preview/login',method='POST',raw=urllib.parse.urlencode({'password':password}))
assert status==200 and '<div id="root">' in body,(status,body[:150])
assert any(c.name=='miraati_preview_session' and c.has_nonstandard_attr('HttpOnly') for c in jar)
if base.startswith('https:'): assert all(c.secure for c in jar)
for route in ('/','/mothers-mirror','/test'):
    status,body,_=call(route);assert status==200 and '<div id="root">' in body
asset=re.search(r'src="([^"]+\.js)"',body).group(1)
status,js,_=call(asset);assert status==200 and 'personaapp-backend.fly.dev' not in js
status,body,_=call('/api/v1/mothers-mirror/journeys',{'timezone':'Europe/Berlin'},'POST')
assert status==200,(status,body[:150])
state=json.loads(body); owner=state['owner_token']; path='/api/v1/mothers-mirror/journeys/'+state['id']
assert call(path,owner='wrong')[0]==404
answers={s['id']:s['options'][0]['id'] for s in state['content']['situations']}
status,body,_=call(path+'/assessments/baseline',{'answers':answers},'PUT',owner)
assert status==200
assert json.loads(call(path,owner=owner)[1])['answers']==answers
assert call(path+'/assessments/baseline',{'answers':answers,'submit':True},'PUT',owner)[0]==200
assert call(path+'/focus',{'focus_code':'connection'},'PUT',owner)[0]==200
assert call(path+'/checkins/1',{'outcome':'difficult','repeat_requested':True},'PUT',owner)[0]==200
resumed=json.loads(call(path,owner=owner)[1]);assert resumed['practice']['day']==1 and resumed['checkins'][0]['outcome']=='difficult'
assert call(path,method='DELETE',owner=owner)[0]==204
assert call(path,owner=owner)[0]==404
# Original quick and deep sections use the same protected backend.
for journey_type in ('quick','deep'):
    status,body,_=call('/api/v1/journey/start',{'journey_type':journey_type},'POST')
    assert status==200,(journey_type,status,body[:150])
assert call('/preview/logout',method='POST')[0]==200
assert call('/api/v1/journey/start',{},'POST')[0]==401
print('PASS: logged-out page/API protection, invalid password, CSRF, HttpOnly session, UI/assets, API destination, owned save/resume/check-in/delete, original quick/deep starts, logout.')
