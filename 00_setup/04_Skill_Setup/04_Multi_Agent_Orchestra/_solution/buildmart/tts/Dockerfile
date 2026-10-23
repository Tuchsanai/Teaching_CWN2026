# BuildMart tts-worker (build context = ROOT)
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    FASTTHAIG2P_HOME=/opt/models/fastthaig2p \
    PYTHAINLP_DATA_DIR=/opt/models/pythainlp-data \
    HF_HOME=/opt/models/hf \
    HEARTBEAT_FILE=/tmp/tts-heartbeat HOME=/tmp
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY tts/requirements.txt .
RUN pip install -r requirements.txt
# download + warm the Thai model at build time so the first request is fast
RUN python -c "from pythaitts import TTS; t=TTS(pretrained='fastthaig2p'); a=t.tts('สวัสดีครับ ราคา 145 บาท', speaker_idx='thai_som', return_type='waveform'); print('thai model ok', len(a))"
COPY tts/textnorm.py tts/worker.py tts/healthcheck.py ./
RUN useradd -r -u 10001 tts && chmod -R a+rX /opt/models
USER tts
HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=4 CMD ["python", "healthcheck.py"]
CMD ["python", "worker.py"]
