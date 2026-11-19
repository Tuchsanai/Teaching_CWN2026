"""Create the test files of TEST-DATA (E3) in this folder. Re-runnable.
usage: python test/data/make_files.py   (base image = results/deploy/test_images/te0000.jpg)"""
import os, shutil, io
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BASE = os.path.join(ROOT, 'results', 'deploy', 'test_images', 'te0000.jpg')
o = lambda n: os.path.join(HERE, n)
MB10 = 10 * 1048576

def pdf(pages):
    objs = ['<< /Type /Catalog /Pages 2 0 R >>']
    kids = ' '.join(f'{3+i} 0 R' for i in range(pages))
    objs.append(f'<< /Type /Pages /Kids [{kids}] /Count {pages} >>')
    for i in range(pages):
        objs.append('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>')
    out = b'%PDF-1.4\n'; offs = []
    for i, ob in enumerate(objs):
        offs.append(len(out)); out += f'{i+1} 0 obj\n{ob}\nendobj\n'.encode()
    x = len(out)
    out += f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()
    for of in offs: out += f'{of:010d} 00000 n \n'.encode()
    out += f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode()
    return out

def main():
    for i in range(1, 102): shutil.copyfile(BASE, o(f'ok-100__{i:03d}.jpg'))
    shutil.copyfile(BASE, o('ok-100.jpg'))
    Image.open(BASE).save(o('ok-100.png'))
    for name in ['conf-089', 'conf-08999', 'conf-090', 'conf-091', 'diff-099', 'diff-100', 'diff-101',
                 'diff-over-101', 'diff-149', 'both-flags', 'total-000', 'total-001', 'total-002',
                 'fail1-then-ok', 'fail2-then-ok', 'fail3', 'conf-089__001', 'conf-089__002']:
        shutil.copyfile(BASE, o(name + '.jpg'))
    data = open(BASE, 'rb').read()
    for name, size in [('size-under', MB10 - 1), ('size-equal', MB10), ('size-over', MB10 + 1)]:
        open(o(name + '.jpg'), 'wb').write(data + b'\0' * (size - len(data)))
    open(o('page-1.pdf'), 'wb').write(pdf(1))
    open(o('page-2.pdf'), 'wb').write(pdf(2))
    open(o('page-0.pdf'), 'wb').write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')   # header only, cannot be opened
    g = io.BytesIO()
    frames = [Image.new('RGB', (40, 40), c) for c in ['red', 'blue']]
    frames[0].save(g, 'GIF', save_all=True, append_images=frames[1:], duration=200, loop=0)
    open(o('anim.gif'), 'wb').write(g.getvalue()); open(o('fake.jpg'), 'wb').write(g.getvalue())
    im = Image.open(BASE).convert('RGB'); w, h = im.size
    im.crop((0, 0, w, h // 2)).save(o('te0000-crop.jpg'), quality=90)
    im.filter(ImageFilter.GaussianBlur(25)).save(o('te0000-blur.jpg'), quality=90)

if __name__ == '__main__':
    main(); print('files:', len(os.listdir(HERE)) - 1)
