import os, sys, time
p = os.environ.get("HEARTBEAT_FILE", "/tmp/tts-heartbeat")
try:
    sys.exit(0 if time.time() - os.path.getmtime(p) < 60 else 1)
except OSError:
    sys.exit(1)
