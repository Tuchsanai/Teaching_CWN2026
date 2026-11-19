# Builds the test files F-1..F-10, R-1..R-8 and N-files into ./fixtures (idempotent).
import os, sys, shutil
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, 'fixtures'); os.makedirs(out, exist_ok=True)
imgs = os.path.normpath(os.path.join(here, '..', '..', 'results', 'deploy', 'test_images'))
base = os.path.join(imgs, '000005_jpg.rf.96e9379ccae638140c4a90fc4b700a2b.jpg')  # reference H=0,V=0
MB = 1048576
def pad(name, size):
    p = os.path.join(out, name)
    data = open(base, 'rb').read()
    assert len(data) < size
    open(p, 'wb').write(data + b'\0' * (size - len(data)))
pad('h0_v0_14_9mb.jpg', 15623782)
pad('h0_v0_15_0mb.jpg', 15 * MB)
pad('h0_v0_15mb_plus1.jpg', 15 * MB + 1)
pad('h0_v0_15_1mb.jpg', 15833498)
shutil.copyfile(base, os.path.join(out, 'h0_v0.jpg'))
Image.open(base).convert('RGB').save(os.path.join(out, 'h0_v0.png'))
im = Image.open(base).convert('RGB'); im.save(os.path.join(out, 'site.gif'))
open(os.path.join(out, 'plan.pdf'), 'wb').write(b'%PDF-1.4\n' + b'0' * 100000 + b'\n%%EOF\n')
open(os.path.join(out, 'fake.jpg'), 'wb').write((b'this is a text file, not a jpg. ' * 40)[:1000])
d = open(base, 'rb').read(); open(os.path.join(out, 'corrupt_half.jpg'), 'wb').write(d[:len(d)//2])
for hv in ['h0_v0','h1_v0','h2_v0','h0_v1','h0_v2','h0_v3','h1_v1','h1_v3']:
    shutil.copyfile(base, os.path.join(out, hv + '.jpg'))
for f in sorted(os.listdir(out)):
    print(f, os.path.getsize(os.path.join(out, f)))
