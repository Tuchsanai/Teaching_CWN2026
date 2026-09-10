#!/usr/bin/env python3
"""Render a Claude Code session .jsonl into USER / ASSISTANT / TOOL lines (secrets masked)."""
import json,sys,re
MASK=[(re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),'<email>')]
def m(s):
    s=str(s)
    for r,rep in MASK: s=r.sub(rep,s)
    return s
n=0
try: lines=open(sys.argv[1],encoding='utf-8').read().splitlines()
except Exception as ex: print("no session file:",ex); sys.exit(0)
for line in lines:
    try: d=json.loads(line)
    except Exception: continue
    t=d.get('type'); msg=d.get('message') or {}
    c=msg.get('content')
    if t=='user':
        if isinstance(c,str): print('USER:',m(c)[:2000])
        elif isinstance(c,list):
            for b in c:
                if b.get('type')=='text': print('USER:',m(b['text'])[:2000])
                elif b.get('type')=='tool_result':
                    r=b.get('content'); 
                    if isinstance(r,list): r=' | '.join(x.get('text','') for x in r if isinstance(x,dict))
                    print('  RESULT:',m(str(r)).replace('\n',' | ')[:600])
    elif t=='assistant' and isinstance(c,list):
        for b in c:
            if b.get('type')=='text' and b['text'].strip(): print('ASSISTANT:',m(b['text'])[:1500])
            elif b.get('type')=='tool_use':
                n+=1; print(f'TOOL {n} {b.get("name")}:',m(json.dumps(b.get("input"),ensure_ascii=False))[:700])
