import sys, os, re
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))
def local(p):
    p = p.strip()
    if p.startswith('/root/workspace/'): p = 'C:/Users/oishi/Documents/GitHub/' + p[len('/root/workspace/'):]
    return p
for out in sys.argv[1:]:
    for line in open(out, encoding='utf-8'):
        if '=' not in line: continue
        tgt, src = line.strip().split('=', 1)
        if src.startswith('FAILED'): print('skip', tgt); continue
        src = local(src); dst = os.path.join(ROOT, tgt)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        maxw = 2400 if tgt.startswith('rooms/') else (768 if tgt.endswith('.png') else 1600)
        if tgt.startswith('therapists/') or tgt.startswith('skin/'): maxw = 900
        if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        if dst.endswith('.jpg'): im.convert('RGB').save(dst, quality=82, optimize=True, progressive=True)
        else: im.save(dst, optimize=True)
        print(tgt, im.size, os.path.getsize(dst)//1024, 'KB')
