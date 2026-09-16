"""Instructor-only portable archive builder; never packages auth, caches, or live state."""
from pathlib import Path
import hashlib,json,zipfile,datetime

ROOT=Path(__file__).resolve().parents[2]
TARGET=ROOT/'Week2-teaching-package.zip'
OMIT_DIRS={'.git','node_modules','__pycache__','test-results','learner-results','.cache','.ipynb_checkpoints'}
OMIT_FILES={'cyolo-build.jsonl','cyolo-build.stderr'} # Parent-owned live orchestration logs stay on disk.

def included(p):
    rel=p.relative_to(ROOT)
    return (p.is_file() and not p.is_symlink() and not any(x in OMIT_DIRS for x in rel.parts)
            and p.name not in OMIT_FILES and p.suffix not in {'.zip','.sha256','.pyc'})

def build():
    files=sorted(p for p in ROOT.rglob('*') if included(p))
    with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,'Week2/'+str(p.relative_to(ROOT)))
    digest=hashlib.sha256(TARGET.read_bytes()).hexdigest()
    TARGET.with_suffix('.sha256').write_text(digest+'  '+TARGET.name+'\n')
    print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'archive':str(TARGET),'files':len(files),'bytes':TARGET.stat().st_size,'sha256':digest}))

if __name__=='__main__':build()
