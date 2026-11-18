"""LAB 9 step: test the worker from outside the machine (old job + 8 jobs at once)."""
import json, sys, threading, time, requests
from concurrent.futures import ThreadPoolExecutor
BASE, KEY, OLD, OUT = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3], sys.argv[4]
H = {"X-API-Key": KEY}
res = {}

# test 1: job left from the previous step
r = requests.get(f"{BASE}/jobs/{OLD}?wait=10", headers=H, timeout=30).json()
img = requests.get(f"{BASE}/jobs/{OLD}/image", headers=H, timeout=30)
open(f"{OUT}/old_job.jpg", "wb").write(img.content)
res["test1_old_job"] = r | {"image_http": img.status_code, "image_bytes": len(img.content)}

# test 2: 8 jobs at the same moment, watch how many images the worker draws at once
peak, stop = [0], threading.Event()
def watch():
    while not stop.is_set():
        for w in requests.get(f"{BASE}/stats", headers=H, timeout=10).json()["workers"]:
            if w.get("alive"): peak[0] = max(peak[0], w.get("working", 0))
        time.sleep(0.1)
threading.Thread(target=watch, daemon=True).start()
prompts = ["a red lighthouse on a cliff at sunset", "a cat astronaut floating in space", "a bowl of ramen, studio photo",
           "a snowy mountain village at night", "a robot gardener watering tulips", "a vintage car on a desert road",
           "an underwater coral city", "a watercolor painting of a fox in a forest"]
def one(i):
    t0 = time.perf_counter()
    j = requests.post(f"{BASE}/jobs", headers=H, json={"prompt": prompts[i]}, timeout=30).json()
    while True:
        s = requests.get(f"{BASE}/jobs/{j['job_id']}?wait=10", headers=H, timeout=30).json()
        if s["status"] in ("done", "dead"): break
    im = requests.get(f"{BASE}/jobs/{j['job_id']}/image", headers=H, timeout=30)
    open(f"{OUT}/job{i+1}.jpg", "wb").write(im.content)
    return {"job_id": j["job_id"], "status": s["status"], "gpu_seconds_per_image": s["seconds"],
            "submit_to_image_seconds": round(time.perf_counter() - t0, 2), "image_http": im.status_code}
time.sleep(0.5)
t = time.perf_counter()
with ThreadPoolExecutor(8) as ex:
    jobs = list(ex.map(one, range(8)))
res["test2_8_jobs"] = {"wall_seconds_all_8": round(time.perf_counter() - t, 2), "peak_working_seen_in_stats": peak[0],
                       "jobs": jobs}
time.sleep(0.3); stop.set()
json.dump(res, open(f"{OUT}/test_worker.json", "w"), indent=2)
print(json.dumps(res, indent=2))
