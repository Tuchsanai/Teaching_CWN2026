import json,sys,os
src,dst=sys.argv[1],sys.argv[2]
out=[]
for line in open(src,encoding='utf-8'):
    o=json.loads(line)
    t=o.get('type')
    if t=='system': continue
    msg=o.get('message',{})
    role=msg.get('role',t)
    c=msg.get('content')
    if isinstance(c,str):
        out.append(f'[{role}] {c[:3000]}'); continue
    for b in c or []:
        bt=b.get('type')
        if bt=='text': out.append(f'[{role}] TEXT: {b["text"][:4000]}')
        elif bt=='tool_use': out.append(f'[{role}] TOOL_USE: {json.dumps(b.get("input"),ensure_ascii=False)[:2500]}')
        elif bt=='tool_result':
            cc=b.get('content')
            s=cc if isinstance(cc,str) else ' '.join(x.get('text','') for x in cc or [])
            out.append(f'[{role}] RESULT: {s[:800]}')
open(dst,'w',encoding='utf-8').write('\n'.join(out))
