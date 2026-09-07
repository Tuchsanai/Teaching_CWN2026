import subprocess,json,sys,base64,time
from pathlib import Path
name=json.loads(Path('work/models-container.json').read_text())['name']
def run(args): subprocess.run(['docker','exec','-e','DISPLAY=:99',name]+args,check=True,stdout=subprocess.DEVNULL)
action=sys.argv[1]
if action.startswith('send:'):
 run(['xdotool','type','--clearmodifiers',action[5:]])
 run(['xdotool','key','Return'])
elif action.startswith('keys:'): run(['xdotool','key']+action[5:].split())
elif action=='paste':
 subprocess.run(['docker','cp','work/comparison-question.txt',name+':/tmp/question.txt'],check=True,stdout=subprocess.DEVNULL)
 run(['bash','-lc','DISPLAY=:99 xclip -selection primary -i /tmp/question.txt'])
 run(['xdotool','key','shift+Insert'])
time.sleep(2)
f=sys.argv[2]
run(['bash','-lc','DISPLAY=:99 import -window $(DISPLAY=:99 xdotool search --onlyvisible --class XTerm | head -1) /tmp/screen.png'])
subprocess.run(['docker','cp',name+':/tmp/screen.png','work/'+f],check=True,stdout=subprocess.DEVNULL)
print(base64.b64encode((Path('work')/f).read_bytes()).decode())
