# ai-box: Whisper (STT) + VoxCPM2 (TTS) + bge-reranker-v2-m3 · เลือกโมเดลด้วย env MODELS=stt | tts,rerank | all
# gcc: torch.compile (triton) ของ VoxCPM2 ต้องคอมไพล์ helper ตอนเริ่ม
# CUDA 12.8 + torch 2.9.1 มี kernel ทั้ง sm_89 (RTX 4090) และ sm_120 (RTX 5090) · driver host ต้อง >= 570
FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 \
    HF_HOME=/hf HF_HUB_ENABLE_HF_TRANSFER=0 \
    LD_LIBRARY_PATH=/opt/conda/lib/python3.11/site-packages/nvidia/cublas/lib:/opt/conda/lib/python3.11/site-packages/nvidia/cudnn/lib
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# ล็อก torch/torchaudio ตาม base image กัน pip อัปเกรดทับ (ไม่งั้นได้ torch ที่ไม่มี sm_120)
RUN python -c "import torch,torchaudio,torchvision;v=lambda m:m.__version__.split('+')[0];print(f'torch=={v(torch)}\ntorchaudio=={v(torchaudio)}\ntorchvision=={v(torchvision)}')" > /tmp/constraints.txt \
    && pip install -r requirements.txt -c /tmp/constraints.txt \
    && python -c "import torch;print('torch',torch.__version__,torch.cuda.get_arch_list() if torch.cuda.is_available() else 'arch-list-at-runtime')"
COPY server.py bench.py make_voice_fixtures.py ./
COPY voices ./voices
EXPOSE 8090
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s CMD curl -sf localhost:8090/health || exit 1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8090", "--workers", "1"]
