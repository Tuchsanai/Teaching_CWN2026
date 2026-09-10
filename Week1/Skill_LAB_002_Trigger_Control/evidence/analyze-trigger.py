#!/usr/bin/env python3
"""Trigger analysis for a lab evidence dir. Claude: Skill tool call in transcript. Codex: SKILL.md read (cat) OR body injected."""
import json,glob,os,sys,re,collections
E=sys.argv[1]; BODY=sys.argv[2] if len(sys.argv)>2 else "ยอดซื้อต่ำกว่า 1000"
rows=[]
for f in sorted(glob.glob(os.path.join(E,"*.summary.jsonl"))):
    for line in open(f,encoding="utf-8"):
        try: d=json.loads(line)
        except: continue
        tag=d["tag"]; cli="claude" if "-claude" in tag else "codex"
        if cli=="claude":
            trig=bool(d.get("skills")); how="Skill tool" if trig else ""
            tr=open(os.path.join(E,tag+".transcript.txt"),encoding="utf-8").read() if os.path.exists(os.path.join(E,tag+".transcript.txt")) else ""
            if not trig and BODY in tr: trig=True; how="pre-rendered (/name)"
        else:
            how=""
            if d.get("skill_reads"): trig=True; how="cat SKILL.md"
            else:
                roll=os.path.join(E,tag+".rollout.jsonl"); trig=False
                if os.path.exists(roll):
                    for l in open(roll,encoding="utf-8"):
                        if BODY in l:
                            try: pl=json.loads(l).get("payload",{})
                            except: pl={}
                            trig=True; how=f"injected ({pl.get('type')}/{pl.get('role')})" if pl.get("type")=="message" else "tool output"; break
        rows.append({"tag":tag,"cli":cli,"trig":trig,"how":how,"wall":d.get("wall_s"),"cost":d.get("cost"),
                     "tokens":(d.get("usage") or {}).get("input_tokens") if cli=="codex" else None,"result":(d.get("result") or "")[:90].replace("\n"," ")})
for r in rows: print(f'{r["tag"]:34} {"YES" if r["trig"] else "no ":4} {r["how"]:28} {r["wall"]:>6}s  {r["result"]}')
# matrix by variant/prompt
m=collections.defaultdict(lambda:[0,0])
for r in rows:
    mm=re.match(r"(.+?)-(P\d|N\d|MANUAL|LIST|A\d|X\d|Q\d|M|C\d|MEM)-(claude|codex)(?:-(\d))?$",r["tag"])
    if not mm: continue
    k=(mm.group(1),mm.group(2),mm.group(3)); m[k][0]+=r["trig"]; m[k][1]+=1
print("\n=== matrix variant | prompt | claude | codex")
for (v,p) in sorted({(k[0],k[1]) for k in m}):
    c=m.get((v,p,"claude")); x=m.get((v,p,"codex"))
    print(f'{v:16} {p:7} {("%d/%d"%tuple(c)) if c else "-":6} {("%d/%d"%tuple(x)) if x else "-":6}')
