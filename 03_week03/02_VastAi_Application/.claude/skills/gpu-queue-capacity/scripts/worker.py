"""LAB 9: GPU worker of the hybrid system (RabbitMQ "jobs" -> SDXL-Turbo -> JPEG for gateway.py).

One process = one GPU. Takes up to 4 waiting jobs at once (prefetch 4) and draws them as one batch,
with the same model and settings as the baseline (SDXL-Turbo, 512x512, 4 steps, guidance 0).
  * ack only after the JPEG is on disk and the "done" event is sent -> a crash mid-batch loses nothing
    (RabbitMQ gives the unacked jobs to the next worker, marked redelivered)
  * empty prompt / unreadable message -> reject(requeue=False) -> dead-letter queue "jobs.dead"
  * heartbeat to gateway every 1 s: state, how many images it is drawing now, total done
Run: python worker.py --gpu 0 [--name gpu0] [--batch 4]
"""
import argparse, asyncio, json, os, socket, time
from pathlib import Path

import aio_pika
import torch
from diffusers import AutoPipelineForText2Image

MODEL, SIZE, STEPS = "stabilityai/sdxl-turbo", 512, 4          # same as baseline (sync_server.py)
AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@127.0.0.1/")
IMAGE_DIR = Path(os.environ.get("IMAGE_DIR", "/workspace/lab9/images"))

ap = argparse.ArgumentParser()
ap.add_argument("--gpu", type=int, required=True, help="GPU index, e.g. 0")
ap.add_argument("--name", default=None, help="worker name shown in gateway /stats")
ap.add_argument("--batch", type=int, default=4, help="max images per batch = RabbitMQ prefetch")
ap.add_argument("--gather-ms", type=int, default=30, help="wait this long for more jobs before drawing")
args = ap.parse_args()
NAME = args.name or f"{socket.gethostname()}-gpu{args.gpu}"
DEVICE = f"cuda:{args.gpu}"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def log(*a):
    print(time.strftime("%H:%M:%S"), NAME, *a, flush=True)

# --- 1) model: load once on the chosen GPU and warm up with a full batch ---
pipe = AutoPipelineForText2Image.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16").to(DEVICE)
pipe.set_progress_bar_config(disable=True)
pipe.vae.enable_slicing()   # decode the batch one image at a time: same pictures, less VRAM (GPU may be shared)

def draw(prompts: list[str]):
    return pipe(prompt=prompts, num_inference_steps=STEPS, guidance_scale=0.0,
                height=SIZE, width=SIZE).images

draw(["warm up"] * args.batch)
log(f"model ready on {DEVICE} ({torch.cuda.get_device_name(args.gpu)})")

state = {"working": 0, "job_id": None, "done": 0}

async def main():
    conn = await aio_pika.connect_robust(AMQP_URL)
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=args.batch)                 # at most 4 unacked jobs in hand
    jobs_q = await ch.declare_queue("jobs", durable=True,      # same arguments as gateway.py
                                    arguments={"x-max-priority": 10, "x-dead-letter-exchange": "jobs.dlx"})
    events = await ch.declare_exchange("jobs.events", aio_pika.ExchangeType.TOPIC, durable=True)

    async def emit(**e):
        e["worker"] = NAME
        await events.publish(aio_pika.Message(json.dumps(e).encode(), content_type="application/json"),
                             routing_key=f"{e['type']}.{NAME}")

    # --- 2) heartbeat every second: alive + how many images are being drawn now ---
    async def heartbeat():
        while True:
            await emit(type="heartbeat", state="busy" if state["working"] else "idle",
                       job_id=state["job_id"], working=state["working"], done=state["done"])
            await asyncio.sleep(1)

    inbox: asyncio.Queue = asyncio.Queue()
    await jobs_q.consume(inbox.put)                             # deliveries land here (max 4 at a time)
    asyncio.create_task(heartbeat())
    loop = asyncio.get_running_loop()
    log(f"waiting for jobs (prefetch {args.batch})")

    while True:
        # --- 3) gather: first job, then whatever else is already waiting, up to 4 ---
        msgs = [await inbox.get()]
        await asyncio.sleep(args.gather_ms / 1000)
        while len(msgs) < args.batch and not inbox.empty():
            msgs.append(inbox.get_nowait())

        batch = []
        for m in msgs:                                          # bad job -> dead-letter queue, not the GPU
            try:
                job = json.loads(m.body)
                prompt = str(job.get("prompt") or "").strip()
                jid = job.get("job_id") or m.message_id
            except Exception:
                job, prompt, jid = {}, "", m.message_id
            if not prompt or not jid:
                await emit(type="failed", job_id=jid, error="empty prompt", requeue=False)
                await m.reject(requeue=False)
                log(f"rejected {jid}: empty prompt -> jobs.dead")
                continue
            batch.append((m, jid, prompt))
        if not batch:
            continue

        for m, jid, _ in batch:
            await emit(type="started", job_id=jid, redelivered=bool(m.redelivered))
        state.update(working=len(batch), job_id=batch[0][1])
        log(f"batch of {len(batch)}: {[j for _, j, _ in batch]}")

        # --- 4) draw the batch on the GPU (in a thread, so heartbeats keep going) ---
        t = time.perf_counter()
        try:
            images = await loop.run_in_executor(None, draw, [p for _, _, p in batch])
        except Exception as e:                                  # e.g. CUDA OOM: retry once, then dead-letter
            for m, jid, _ in batch:
                again = not m.redelivered
                await emit(type="failed", job_id=jid, error=f"{type(e).__name__}", requeue=again)
                await m.nack(requeue=again)
            log(f"batch failed: {type(e).__name__}: {e}")
            state.update(working=0, job_id=None)
            continue
        per_image = (time.perf_counter() - t) / len(batch)

        # --- 5) save -> tell gateway -> ack (ack is last, so nothing is lost on a crash) ---
        for (m, jid, _), img in zip(batch, images):
            path = IMAGE_DIR / f"{jid}.jpg"
            tmp = path.with_suffix(".tmp")
            img.save(tmp, format="JPEG", quality=90)
            os.replace(tmp, path)                               # whole file appears at once
            await emit(type="done", job_id=jid, seconds=round(per_image, 3), image=str(path),
                       batch=len(batch))
            await m.ack()
            state["done"] += 1
        log(f"done {len(batch)} in {per_image * len(batch):.2f}s ({per_image:.3f}s/image)")
        state.update(working=0, job_id=None)

asyncio.run(main())
