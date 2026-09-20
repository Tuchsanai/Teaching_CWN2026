#!/bin/bash
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv ffmpeg espeak-ng git > /dev/null
python3 -m venv /root/venv
/root/venv/bin/pip install -q --upgrade pip
/root/venv/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cu124
/root/venv/bin/pip install -q faster-whisper transformers sentencepiece sacremoses accelerate yt-dlp soundfile "mcp[cli]" uvicorn starlette
/root/venv/bin/pip install -q kokoro "misaki[zh]" pypinyin
/root/venv/bin/python -c "import torch;print('torch',torch.__version__,torch.cuda.is_available())"
echo SETUP_DONE
