import json, time, urllib.request, subprocess, threading
key = open('/workspace/lab7/secrets/api_key').read().strip()
def gpu():
    return subprocess.check_output(['nvidia-smi','-i','0','--query-gpu=temperature.gpu,clocks.sm,clocks.max.sm,utilization.gpu','--format=csv,noheader,nounits']).decode().strip()
print('idle GPU0 (temp,clock,maxclock,util):', gpu())
samples = []
stop = False
def mon():
    while not stop:
        samples.append(gpu()); time.sleep(0.5)
qs = ["น้ำยาล้างจานแบบไหนอ่อนโยนต่อมือคะ","ปลั๊กพ่วงแบบไหนมีระบบกันไฟกระชากครับ","ผ้าขี้ริ้วแบบไหนซับน้ำได้ดีคะ"]
th = threading.Thread(target=mon); th.start()
for q in qs:
    body = json.dumps({"model":"shop-bot","messages":[{"role":"user","content":q}],"max_tokens":150,"stream":True,"stream_options":{"include_usage":True}}).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/v1/chat/completions', body, {'Content-Type':'application/json','Authorization':'Bearer '+key})
    t0 = time.time(); first = None; toks = 0
    with urllib.request.urlopen(req) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith('data:') or line.endswith('[DONE]'): continue
            d = json.loads(line[5:])
            if d.get('choices') and d['choices'][0]['delta'].get('content') and first is None: first = time.time()
            if d.get('usage'): toks = d['usage']['completion_tokens']
    t1 = time.time()
    print(f'Q: TTFT={first-t0:.3f}s tokens={toks} speed={(toks-1)/(t1-first):.1f} tok/s total={t1-t0:.2f}s')
stop = True; th.join()
c = [list(map(float, s.split(','))) for s in samples]
busy = [x for x in c if x[3] > 50] or c
print('under load GPU0: temp max %.0f C, clock avg %.0f MHz (max %.0f)' % (max(x[0] for x in busy), sum(x[1] for x in busy)/len(busy), busy[0][2]))
