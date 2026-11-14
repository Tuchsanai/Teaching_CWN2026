import json,sys,glob,os
out=sys.argv[1]
for path in sorted(glob.glob(sys.argv[2]+'/*.jsonl')):
    name=os.path.basename(path).replace('.jsonl','')
    with open(os.path.join(out,name+'.txt'),'w') as o:
        for line in open(path):
            d=json.loads(line)
            t=d.get('type')
            if t=='system':
                if d.get('subtype')!='thinking_tokens': o.write(f"[SYSTEM {d.get('subtype')}]\n")
                continue
            msg=d.get('message',{})
            content=msg.get('content') if isinstance(msg,dict) else None
            if isinstance(content,str):
                o.write(f"[{t}] {content}\n"); continue
            for c in content or []:
                ct=c.get('type')
                if ct=='text': o.write(f"[{t} TEXT] {c['text']}\n")
                elif ct=='tool_use': o.write(f"[{t} TOOL_USE {c.get('name')}] {json.dumps(c.get('input'),ensure_ascii=False)}\n")
                elif ct=='tool_result':
                    cc=c.get('content')
                    if isinstance(cc,list): cc='\n'.join(x.get('text','') for x in cc if isinstance(x,dict))
                    o.write(f"[RESULT] {cc}\n")
                elif ct=='thinking':
                    o.write(f"[THINK] {c.get('thinking','')[:400]}\n")
                else: o.write(f"[{t} {ct}]\n")
            if d.get('type')=='result':
                o.write(f"[RESULT_FINAL] {json.dumps({k:v for k,v in d.items() if k!='message'},ensure_ascii=False)[:500]}\n")
