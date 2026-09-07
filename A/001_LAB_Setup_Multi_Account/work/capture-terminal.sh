#!/bin/bash
set -eu
export DISPLAY=:99
Xvfb :99 -screen 0 1440x700x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &
sleep 1
mkdir -p /workspace/lab001
export PS1='student@ubuntu:~/lab001$ '
xterm -geometry 110x24 -fa 'DejaVu Sans Mono' -fs 15 -bg '#151c29' -fg '#e1e7f0' -xrm 'XTerm*allowTitleOps: false' -title 'Ubuntu Terminal - Claude Code setup' -e bash --noprofile --norc >/tmp/xterm.log 2>&1 &
sleep 2
xdotool type --clearmodifiers 'cd /workspace/lab001'
xdotool key Return
sleep 1
xdotool type --clearmodifiers 'clear'
xdotool key Return
sleep 1
xdotool type --clearmodifiers 'curl -fsSL https://claude.ai/install.sh | bash'
import -window root /tmp/terminal-install-claude.png
xdotool key Return
