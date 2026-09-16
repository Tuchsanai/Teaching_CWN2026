"""Read executable lesson instructions from the single learner guide."""
from pathlib import Path
import re
from lab_paths import LAB_DIRS

def read_dataset(root, lab, variant):
    """Extract the exact dataset, excluding the surrounding guide and answers."""
    if variant not in ('A', 'B', 'C'):
        raise ValueError('Unknown dataset variant')
    guide=(Path(root)/LAB_DIRS[lab]/'README.md').read_text()
    start=f'<!-- lab-data:{variant}:start -->\n````text\n'
    end=f'````\n<!-- lab-data:{variant}:end -->'
    if guide.count(start)!=1 or guide.count(end)!=1:
        raise ValueError(f'Missing or duplicate dataset {variant} in {lab}')
    return guide.split(start,1)[1].split(end,1)[0]

def shift_headings(text, delta):
    lines=[]; fence=None
    for line in text.splitlines(keepends=True):
        match=re.match(r'^\s*(`{3,}|~{3,})',line)
        if match:
            token=match.group(1)
            if fence is None: fence=(token[0],len(token))
            elif token[0]==fence[0] and len(token)>=fence[1]: fence=None
        elif fence is None:
            match=re.match(r'^(#{1,6})(\s+)',line)
            if match: line='#'*(len(match[1])+delta)+line[len(match[1]):]
        lines.append(line)
    return ''.join(lines)

def read_section(root, lab, section):
    guide=(Path(root)/LAB_DIRS[lab]/'README.md').read_text()
    start=f'<!-- lab-content:{section}:start -->\n'
    end=f'<!-- lab-content:{section}:end -->'
    if guide.count(start)!=1 or guide.count(end)!=1:
        raise ValueError(f'Missing or duplicate {section} section in {lab} guide')
    return shift_headings(guide.split(start,1)[1].split(end,1)[0],-1)
