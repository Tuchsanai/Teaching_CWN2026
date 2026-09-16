"""Instructor-only extraction smoke test. No AI calls. Dedicated port/state, always stopped."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,tempfile,urllib.request,zipfile

ROOT=Path(__file__).resolve().parents[2]
steps=[]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
report={'utc_start':utc(),'kind':'extracted ZIP functional smoke; browser suite tested original same core files',
        'port':18764,'steps':steps,'ai_calls':0}
with tempfile.TemporaryDirectory(prefix='week2-zip-smoke-') as tmp:
    tmp=Path(tmp)
    with zipfile.ZipFile(ROOT/'Week2-teaching-package.zip') as z:
        assert z.testzip() is None
        report['crc_pass']=True
        names=z.namelist()
        assert all(not any(x in Path(n).parts for x in ['node_modules','.git','__pycache__','learner-results','test-results']) for n in names)
        assert not any(Path(n).name in ['cyolo-build.jsonl','cyolo-build.stderr'] for n in names)
        report['excluded_state_and_parent_logs']=True
        report['launcher_executable_bits']={n:bool((z.getinfo('Week2/'+n).external_attr>>16)&0o111) for n in ['shop','learn']}
        assert all(report['launcher_executable_bits'].values())
        z.extractall(tmp)
    package=tmp/'Week2'
    env=dict(os.environ,WEEK2_SHOP_STATE=str(tmp/'isolated-state'))
    def run(*argv,expected=0):
        r=subprocess.run(list(argv),cwd=package,env=env,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=20)
        steps.append({'utc':utc(),'argv':list(argv),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        assert r.returncode==expected,steps[-1]
        return r.stdout
    try:
        run('python3','instructor/runtime/provision_shop.py','--port','18764')
        run('sh','shop','preflight')
        run('sh','shop','reset','basic-A')
        assert 'STOPPED' in run('sh','shop','status')
        try:urllib.request.urlopen('http://127.0.0.1:18764',timeout=2);raise AssertionError('expected stopped')
        except urllib.error.URLError:report['before_connection_refused']=True
        run('sh','shop','start')
        assert 'CHECK PASS' in run('sh','shop','check')
        with urllib.request.urlopen('http://127.0.0.1:18764/api/bookings') as r:bookings=json.load(r)
        assert len(bookings['items'])==1 and bookings['items'][0]['version']=='v1'
        report['server_verified_booking']=bookings
        run('sh','shop','reset','advanced-B')
        run('sh','shop','check',expected=1)
        run('sh','shop','rollback')
        assert 'CHECK PASS' in run('sh','shop','check')
        report['core_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [ROOT/'index.html',ROOT/'shop',ROOT/'learn',ROOT/'instructor/runtime/shop_runtime.py',
          *sorted((ROOT/'.agents/skills').glob('*/SKILL.md'))]}
        for p,h in report['core_hashes'].items():assert hashlib.sha256((package/p).read_bytes()).hexdigest()==h
        report['native_skills_packaged']=3
        report['pass']=True
    finally:
        run('sh','shop','stop')
        report['final_status']=run('sh','shop','status').strip()
report['temporary_workspace_removed']=True
report['utc_end']=utc()
(ROOT/'evidence/build/zip-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['steps','core_hashes','server_verified_booking']},ensure_ascii=False,indent=2))
