import json, sys
path = sys.argv[1]
maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 400
for line in open(path, encoding='utf-8'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    t = d.get('type')
    if t == 'system':
        print(f"[system:{d.get('subtype')}]")
        continue
    if t == 'result':
        r = d.get('result', '')
        print(f"[RESULT] turns={d.get('num_turns')} cost={d.get('total_cost_usd')}\n{str(r)[:maxlen*3]}")
        continue
    msg = d.get('message', {})
    content = msg.get('content', [])
    if isinstance(content, str):
        print(f"[{t}] {content[:maxlen]}")
        continue
    for c in content:
        ct = c.get('type')
        if ct == 'text':
            print(f"[{t}/text] {c['text'][:maxlen]}")
        elif ct == 'tool_use':
            inp = json.dumps(c.get('input', {}), ensure_ascii=False)
            print(f"[tool_use:{c.get('name')}] {inp[:maxlen]}")
        elif ct == 'tool_result':
            cc = c.get('content')
            if isinstance(cc, list):
                cc = ' '.join(x.get('text', '') for x in cc if isinstance(x, dict))
            print(f"[tool_result] {str(cc)[:maxlen]}")
