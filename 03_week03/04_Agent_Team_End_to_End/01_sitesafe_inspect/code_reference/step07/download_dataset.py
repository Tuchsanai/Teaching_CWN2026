"""Download Roboflow dataset construction-site-safety v28 (YOLO format) onto the rented machine.
The API key is read from the environment variable ROBOFLOW_API_KEY and is never printed."""
import io, json, os, sys, urllib.request, zipfile

DEST = sys.argv[1] if len(sys.argv) > 1 else "/workspace/e2e_sitesafe/dataset"
WORKSPACE, PROJECT, VERSION, FMT = "roboflow-universe-projects", "construction-site-safety", 28, "yolov11"
key = os.environ["ROBOFLOW_API_KEY"]

def get_link(fmt):
    url = f"https://api.roboflow.com/{WORKSPACE}/{PROJECT}/{VERSION}/{fmt}?api_key={key}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except Exception as e:  # never show the URL (it contains the key)
        print("request failed:", type(e).__name__, getattr(e, "code", ""))
        return None

info = None
for fmt in (FMT, "yolov8"):
    info = get_link(fmt)
    if info and "export" in info:
        print("export format:", fmt)
        break
if not info or "export" not in info:
    sys.exit("could not get export link")

os.makedirs(DEST, exist_ok=True)
zpath = os.path.join(DEST, "dataset.zip")
urllib.request.urlretrieve(info["export"]["link"], zpath)
print("zip size MB:", round(os.path.getsize(zpath) / 1e6, 1))
with zipfile.ZipFile(zpath) as z:
    z.extractall(DEST)
os.remove(zpath)
print("extracted to", DEST, "->", sorted(os.listdir(DEST)))
print("DOWNLOAD_DONE")
