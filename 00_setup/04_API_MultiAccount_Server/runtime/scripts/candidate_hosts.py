#!/usr/bin/env python3
"""Print host names/IPs that devtools might use to reach ports published on the Docker host.
Nothing here is trusted: deploy.sh / the tests use a candidate only after /health answers on it.
Usage: candidate_hosts.py DOCKER_HOST"""
import socket
import struct
import sys
from urllib.parse import urlparse

out = []
target = sys.argv[1] if len(sys.argv) > 1 else ""
u = urlparse(target)
if u.scheme in ("tcp", "ssh", "http", "https") and u.hostname:
    out.append(u.hostname)
# Docker Desktop's documented name for the host; only listed if it resolves here.
for name in ("host.docker.internal",):
    try:
        socket.getaddrinfo(name, None)
        out.append(name)
    except OSError:
        pass
# default gateway of this container (usually the Docker host's bridge address)
try:
    for line in open("/proc/net/route").read().splitlines()[1:]:
        f = line.split()
        if f[1] == "00000000":
            out.append(socket.inet_ntoa(struct.pack("<L", int(f[2], 16))))
except OSError:
    pass
out.append("127.0.0.1")  # works only if the daemon shares this network namespace
print("\n".join(dict.fromkeys(out)))
