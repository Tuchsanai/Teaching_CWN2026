#!/usr/bin/env python3
import json,sys,re
def m(s): return re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+','<email>',str(s))
n=0
for line in open(sys.argv[1],encoding='utf-8'):
    try: d=json.loads(line)
    except Exception: continue
    t=d.get('type'); it=d.get('item') if isinstance(d.get('item'),dict) else {}
    if t=='item.completed':
        k=it.get('type')
        if k=='command_execution':
            n+=1; print(f'CMD {n}:',m(it.get('command',''))[:400]); print('  OUT:',m(it.get('aggregated_output',''))[:500].replace('\n',' | '), '| exit',it.get('exit_code'))
        elif k=='agent_message': print('ASSISTANT:',m(it.get('text',''))[:1500])
        elif k=='reasoning': print('REASONING:',m(it.get('text',''))[:300])
        elif k in ('file_change','mcp_tool_call','web_search'): print(f'{k.upper()}:',m(json.dumps(it,ensure_ascii=False))[:400])
    elif t=='turn.completed': print('USAGE:',json.dumps(d.get('usage')))
    elif t=='turn.failed': print('FAILED:',m(json.dumps(d.get('error'),ensure_ascii=False)))
