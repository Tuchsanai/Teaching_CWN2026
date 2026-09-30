#!/bin/bash
W=/root/workspace/CWN/Teaching/00_setup/.work/06_pwcli
kill $(pgrep -x x11vnc) $(pgrep -x Xvfb) 2>/dev/null; sleep 1
Xvfb :99 -screen 0 1928x1200x24 >$W/logs/xvfb.log 2>&1 &
sleep 1
x11vnc -display :99 -rfbport 5999 -localhost -forever -shared -nopw -quiet >$W/logs/x11vnc.log 2>&1 &
