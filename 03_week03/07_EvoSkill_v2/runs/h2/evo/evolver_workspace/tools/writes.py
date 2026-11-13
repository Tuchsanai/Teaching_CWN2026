import json,sys
for l in open(sys.argv[1]):
    d=json.loads(l)
    if d.get('type')=='assistant':
        for c in d['message'].get('content',[]):
            if c.get('type')=='tool_use' and c.get('name') in ('Write','Edit'):
                i=c['input']
                print('---',c['name'],i.get('file_path'))
                print(i.get('content') or ('OLD:'+i.get('old_string','')+'\nNEW:'+i.get('new_string','')))
