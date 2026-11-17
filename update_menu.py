import datetime as dt
import json
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

URL = 'https://lounastaja.app/api/v1/rss/week/9c1a2cdf-0bf6-4716-84ea-f4b8673d4240/active?language=fi'

class Lines(HTMLParser):
    def __init__(self):
        super().__init__(); self.lines=[]; self.current=''
    def handle_data(self, data): self.current += data
    def handle_starttag(self, tag, attrs):
        if tag == 'br': self.flush()
    def flush(self):
        if self.current.strip(): self.lines.append(self.current.strip())
        self.current=''

with urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent':'MidagonLunchDisplay/1.0'}), timeout=25) as r:
    root=ET.fromstring(r.read())
items=[]
for item in root.findall('./channel/item'):
    p=Lines(); p.feed(item.findtext('description') or ''); p.flush()
    pub=item.findtext('pubDate') or ''
    from email.utils import parsedate_to_datetime
    date=parsedate_to_datetime(pub).date().isoformat()
    items.append({'date':date,'title':(item.findtext('title') or '').strip(),'lines':p.lines})
if not items: raise RuntimeError('RSS-syote ei sisalla ruokalistaa')
Path(__file__).with_name('menu.json').write_text(json.dumps({'updated':dt.datetime.now(dt.timezone.utc).isoformat(),'items':items},ensure_ascii=False,indent=2),encoding='utf-8')
