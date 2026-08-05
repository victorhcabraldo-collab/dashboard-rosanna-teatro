# -*- coding: utf-8 -*-
import re, sys, json, urllib.request, os

APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxLhWmSBgvuB_UxKx1ZxoDhFBjP-tqxSqdpGlWrcOpXJExRbigyqb1vFlamxBO38EXyLw/exec'
DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, 'template.html')
OUTPUT = os.path.join(DIR, 'index.html')

print('Fetching data from Apps Script...')
req = urllib.request.Request(APPS_SCRIPT_URL, headers={'User-Agent': 'DashboardBuilder/1.0'})
resp = urllib.request.urlopen(req, timeout=120)
data = json.loads(resp.read().decode('utf-8'))

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

html = re.sub(
    r'^const META_ROWS\s*=\s*\[.*?\];',
    'const META_ROWS = ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';',
    html, count=1, flags=re.MULTILINE | re.DOTALL
)
html = re.sub(
    r'^const HOT_ROWS\s*=\s*\[.*?\];',
    'const HOT_ROWS = ' + json.dumps(hot, ensure_ascii=False, separators=(',', ':')) + ';',
    html, count=1, flags=re.MULTILINE | re.DOTALL
)
html = re.sub(r'const DATA_GERACAO\s*=\s*"[^"]*";', f'const DATA_GERACAO = "{dg}";', html, count=1)
html = re.sub(r'const DATA_INICIO\s*=\s*"[^"]*";', f'const DATA_INICIO = "{di}";', html, count=1)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Saved: index.html ({os.path.getsize(OUTPUT)/1024:.0f} KB)')
