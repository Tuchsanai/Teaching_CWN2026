import json,sys
path=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 300
for l in open(path):
    d=json.loads(l)
    t=d.get('type')
    if t=='assistant':
        for c in d['message'].get('content',[]):
            if c.get('type')=='text': print('A:',c['text'][:lim*3])
            elif c.get('type')=='tool_use': print('TOOL_USE:',c.get('name'),json.dumps(c.get('input'),ensure_ascii=False)[:lim*3])
            elif c.get('type')=='thinking': pass
    elif t=='user':
        m=d['message'].get('content')
        if isinstance(m,str): print('U:',m[:lim*3])
        else:
            for c in m:
                if c.get('type')=='tool_result':
                    cc=c.get('content')
                    s=cc if isinstance(cc,str) else json.dumps(cc,ensure_ascii=False)
                    print('RESULT:',s[:lim])
                elif c.get('type')=='text': print('U:',c['text'][:lim*3])
    elif t=='result':
        print('RESULT_FINAL:',str(d.get('result',''))[:lim*3], d.get('terminal_reason'))
