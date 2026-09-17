"""N5 merger. Run only after all dependency records report DONE."""
import json
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
class DOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.external = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('src', 'href'):
            if attrs.get(key, '').startswith(('https:', 'http:', '//')):
                self.external.append(attrs[key])

for node in ('N1','N1b','N2','N3','N4'):
    record = json.loads((ROOT / 'nodes' / (node+'.json')).read_text())
    assert set(record) == {'node','status','output','assumptions'}, (node, 'Invalid result contract')
    assert record['node'] == node and record['status'] == 'DONE', (node, 'Dependency not DONE')
    assert isinstance(record['output'], str) and isinstance(record['assumptions'], list)
html = (ROOT/'nodes/N3.html').read_text()
js = (ROOT/'nodes/N2.js').read_text()
assert html.count('<!-- APP_SCRIPT -->') == 1, 'Template integration marker mismatch'
assert '</script' not in js.lower(), 'Unsafe inline script terminator'
dom = DOM()
dom.feed(html)
assert len(dom.ids) == len(set(dom.ids)), 'Duplicate static DOM IDs'
required = '''app-notice screen-rooms room-list screen-availability availability-form availability-room availability-date availability-start availability-end availability-submit availability-result availability-schedule screen-book booking-form booking-room booking-date booking-start booking-end booking-title booking-submit booking-result screen-bookings booking-list nav-rooms nav-availability nav-book nav-bookings'''.split()
assert set(required) <= set(dom.ids), f'Missing DOM IDs: {set(required)-set(dom.ids)}'
assert not dom.external, f'External URLs: {dom.external}'
output = html.replace('<!-- APP_SCRIPT -->', '<script>\n'+js+'\n</script>')
(ROOT/'output.html').write_text(output)
print(json.dumps({'merged':'output.html','dependency_status':'all DONE','static_ids_checked':len(required),'duplicate_ids':False,'external_asset_urls':dom.external}, ensure_ascii=False))
