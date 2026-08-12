# -*- coding: utf-8 -*-
import re, sys, json, urllib.request, os, time

APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxLhWmSBgvuB_UxKx1ZxoDhFBjP-tqxSqdpGlWrcOpXJExRbigyqb1vFlamxBO38EXyLw/exec'
DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, 'template.html')
OUTPUT = os.path.join(DIR, 'index.html')
MAX_RETRIES = 3

def fetch_with_redirects(url, max_redirects=5):
    for _ in range(max_redirects):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; DashboardBuilder/1.0)'})
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            return resp.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308):
                url = e.headers.get('Location', url)
                continue
            raise
    raise Exception('Too many redirects')

print('Fetching data from Apps Script...')
data = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        raw = fetch_with_redirects(APPS_SCRIPT_URL)
        data = json.loads(raw)
        break
    except Exception as e:
        print(f'  Attempt {attempt}/{MAX_RETRIES} failed: {e}')
        if attempt < MAX_RETRIES:
            time.sleep(15)
if data is None:
    print('ERROR: All fetch attempts failed')
    sys.exit(1)

if 'error' in data:
    print(f'ERROR: {data["error"]}')
    sys.exit(1)

meta = data.get('meta_rows', [])
hot = data.get('hotmart_rows', [])
dg = data.get('data_geracao', '')
di = data.get('data_inicio', '')
print(f'  Meta: {len(meta)} rows | Hotmart: {len(hot)} rows | Hasta: {dg}')

with open(TEMPLATE, encoding='utf-8') as f:
    html = f.read()

meta_js = json.dumps(meta, ensure_ascii=False, separators=(',', ':'))
hot_js = json.dumps(hot, ensure_ascii=False, separators=(',', ':'))
html = re.sub(
    r'^const META_ROWS\s*=\s*\[.*?\];',
    lambda m: 'const META_ROWS = ' + meta_js + ';',
    html, count=1, flags=re.MULTILINE | re.DOTALL
)
html = re.sub(
    r'^const HOT_ROWS\s*=\s*\[.*?\];',
    lambda m: 'const HOT_ROWS = ' + hot_js + ';',
    html, count=1, flags=re.MULTILINE | re.DOTALL
)
html = re.sub(r'const DATA_GERACAO\s*=\s*"[^"]*";', f'const DATA_GERACAO = "{dg}";', html, count=1)
html = re.sub(r'const DATA_INICIO\s*=\s*"[^"]*";', f'const DATA_INICIO = "{di}";', html, count=1)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Saved: index.html ({os.path.getsize(OUTPUT)/1024:.0f} KB)')
