#!/bin/bash
W=/root/workspace/CWN/Teaching/00_setup/.work/06_pwcli/img_gen
cd $W
while IFS="|" read -r name prompt; do
  [ -z "$name" ] && continue
  [ -s "$W/$name" ] && continue
  echo "== $name $(date +%T)" >> $W/run.log
  timeout 900 cyolo1 exec --skip-git-repo-check "Use your built-in image generation tool to create ONE image (landscape 1536x1024 PNG). Save it exactly to $W/$name . Do not create any other files. Image description: $prompt" < /dev/null >> $W/run.log 2>&1
  ls -la "$W/$name" >> $W/run.log 2>&1
done < $W/prompts.txt
echo ALLDONE >> $W/run.log
