"""Read-only package audit, with evidence report written under Week2/evidence/build."""
from pathlib import Path
from lab_paths import LAB_DIRS
from lab_content import read_section
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import hashlib,json,datetime,re
ROOT=Path(__file__).resolve().parents[2]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[];self.assets=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id' in d:self.ids.append(d['id'])
  if 'href' in d and t=='a':self.links.append(d['href'])
  if t in ['script','img','link']:
   x=d.get('src') if t!='link' else d.get('href')
   if x:self.assets.append(x)
errors=[];checked=0
for p in ROOT.rglob('*.html'):
 if any(x in p.parts for x in ['initial-failure','test-results','.ipynb_checkpoints']):continue
 doc=Links();doc.feed(p.read_text())
 for x in doc.links:
  u=urlsplit(x)
  if u.scheme or u.netloc:continue
  f=(p.parent/unquote(u.path)).resolve() if u.path else p
  if not f.exists():errors.append({'file':str(p.relative_to(ROOT)),'href':x,'error':'missing target'});continue
  if u.fragment and f.suffix=='.html':
   target=Links();target.feed(f.read_text())
   if unquote(u.fragment) not in target.ids:errors.append({'file':str(p.relative_to(ROOT)),'href':x,'error':'missing anchor'})
  checked+=1
p=Links();p.feed((ROOT/'index.html').read_text())
assets=[x for x in p.assets if not x.startswith('data:')]
if assets:errors.append({'error':'slides depend on assets','assets':assets})
names={'lab1':'shop-requirements','lab2':'shop-recovery','lab3':'shop-complaints'};skills={}
for lab,name in names.items():
 s=(ROOT/f'.agents/skills/{name}/SKILL.md').read_text();body=s.split('---',2)[2].strip();procedure=read_section(ROOT,lab,'skill').strip()
 skills[lab]={'body_equals_baseline':body==procedure,'name_valid':bool(re.search(r'^name: '+name+'$',s,re.M)),'text_only':not (ROOT/f'.agents/skills/{name}/scripts').exists()}
 if not all(skills[lab].values()):errors.append({'error':'skill consistency','lab':lab})
runs=[]
for m in sorted((ROOT/'evidence/experiments').glob('*/metadata.json')):
 d=json.loads(m.read_text());snap=m.parent/'input-snapshot';manifest=json.loads((m.parent/'input-manifest.json').read_text())
 hashes=all(hashlib.sha256((snap/p).read_bytes()).hexdigest()==h for p,h in manifest.items())
 cmds=[x.get('command','') for x in d.get('tool_commands',[]) if x.get('exit_code') is not None]
 run={'label':d['label'],'success':d['success'],'snapshot_hashes_match':hashes,'native_read':d['native_read_confirmed'],'commands':cmds,'model_effort_correct':d['model']=='gpt-6-astra' and d['effort']=='high' and d['command_argv'][:2]==['cyolo1','exec'],'raw_answer':(m.parent/'answer.md').exists()}
 runs.append(run)
 if not hashes or not run['model_effort_correct']:errors.append({'error':'run integrity','label':d['label']})
old=json.loads((ROOT/'evidence/build/week1-before.json').read_text());changes=[]
for f,h in old.items():
 # Original manifest paths were relative to Teaching.
 p=ROOT.parent/f
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:changes.append(f)
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local_link_targets_checked':checked,'errors':errors,'slides_external_assets':assets,'skills':skills,'runs':runs,'week1_changes_since_start':changes,'week1_files_checked':len(old)}
(ROOT/'evidence/build/package-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['utc','local_link_targets_checked','errors','skills','week1_changes_since_start','week1_files_checked']},ensure_ascii=False,indent=2))
