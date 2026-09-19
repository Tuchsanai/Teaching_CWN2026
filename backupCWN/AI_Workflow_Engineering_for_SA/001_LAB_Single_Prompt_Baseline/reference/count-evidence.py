"""Count primary table rows, not incidental references or traceability claims."""
from pathlib import Path
import collections, hashlib, json, re

lab = Path(__file__).resolve().parent.parent
def rows(path, prefix):
    result=[]
    heading=''
    for line_number,line in enumerate(path.read_text().splitlines(),1):
        if line.startswith('#'):
            heading=line
        if re.match(r'^\|\s*'+prefix+r'-\d\d\s*\|',line):
            cells=[c.strip() for c in line.strip('|').split('|')]
            result.append(dict(id=cells[0],line=line_number,heading=heading,cells=cells))
    return result

source=rows(lab/'input/user-stories.md','US')
analysis=rows(lab/'reference/step-01/round-1/us-analysis.md','US')
draft=lab/'reference/step-02/round-1/fr-nfr-v0.md'
fr=rows(draft,'FR')
nfr=rows(draft,'NFR')
coverage={r['id']:[f['id'] for f in fr if r['id'] in re.findall(r'US-\d\d',f['cells'][1])] for r in source}
roles={}
for row in source:
    roles.setdefault(row['cells'][1],[]).append(row['id'])
before=json.loads((lab/'reference/input-sha256-before.json').read_text())
unchanged={p:hashlib.sha256((lab/p).read_bytes()).hexdigest()==sha for p,sha in before.items()}
result=dict(source_us_count=len(source), source_roles=roles, analysis_primary_rows=len(analysis),
            analysis_rows=[{k:r[k] for k in ['id','line','heading']} for r in analysis],
            analysis_missing=sorted(set(r['id'] for r in source)-set(r['id'] for r in analysis)),
            analysis_duplicate_ids=[k for k,v in collections.Counter(r['id'] for r in analysis).items() if v>1],
            fr_count=len(fr),nfr_count=len(nfr),fr_rows=fr,nfr_rows=nfr,us_to_fr=coverage,
            missing_fr_us=[u for u,ids in coverage.items() if not ids],input_hashes_unchanged=unchanged)
source_by_id={r['id']:r for r in source}
result['fr_ac_matches_source']={r['id']:source_by_id[r['cells'][1]]['cells'][5]==r['cells'][3] for r in fr}
result['nfr_ac_matches_source']={r['id']:source_by_id[r['cells'][1]]['cells'][5]==r['cells'][3] for r in nfr}
result['nfr_by_category']=dict(collections.Counter(r['heading'] for r in nfr))
print(json.dumps(result,ensure_ascii=False,indent=2))
