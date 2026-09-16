# Instructor only. Additional native gate confirmation disclosed in build report.
from experiments import run
for lab in ['lab1','lab3']:
 for variant in ['B','A']:
  m=run(lab,variant,'S',f'{lab}-{variant}-S-confirmed')
  if not m['success'] or not m['native_read_confirmed']:raise SystemExit('STOP: failure or native read unconfirmed, no automatic retry')
for variant,condition in [('A','P'),('B','S'),('A','S'),('B','P')]:
 m=run('lab2',variant,condition,f'lab2-{variant}-{condition}')
 if not m['success'] or (condition=='S' and not m['native_read_confirmed']):raise SystemExit('STOP: no retry')
