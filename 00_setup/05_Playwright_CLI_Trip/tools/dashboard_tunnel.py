"""LAB05 dashboard tunnel: 127.0.0.1:9230 (local) -> SSH -> docker exec devtools -> 127.0.0.1:9230 (container).

Raw byte relay only (HTTP + WebSocket pass through untouched). Requires env:
LAB05_SSH_PASSWORD, LAB05_SSH_HOSTKEY (base64), LAB05_SSH_KEYTYPE (e.g. ssh-ed25519).
"""
import base64, os, shlex, socket, socketserver, sys, threading
import paramiko

LOCAL = ("127.0.0.1", 9230)
SSH_HOST, SSH_PORT, SSH_USER = "127.0.0.1", 22022, "root"
CHUNK = 65536

RELAY = r"""
import os,socket,threading
s=socket.create_connection(('127.0.0.1',9230))
def up():
    try:
        while True:
            d=os.read(0,65536)
            if not d: break
            s.sendall(d)
    except OSError: pass
    try: s.shutdown(socket.SHUT_WR)
    except OSError: pass
threading.Thread(target=up,daemon=True).start()
try:
    while True:
        d=s.recv(65536)
        if not d: break
        while d: d=d[os.write(1,d):]
except OSError: pass
"""
CMD = shlex.join(["docker", "exec", "-i", "devtools", "python3", "-u", "-c", RELAY])

_secret = ""


def err(where, e):
    msg = type(e).__name__
    if not isinstance(e, paramiko.BadHostKeyException):
        detail = str(e).replace(_secret, "***") if _secret else str(e)
        msg += ": " + detail[:200]
    print(f"ERROR [{where}] {msg}", file=sys.stderr, flush=True)


def load_key(keytype, b64):
    data = base64.b64decode(b64)
    if hasattr(paramiko.PKey, "from_type_string"):
        return paramiko.PKey.from_type_string(keytype, data)
    cls = {"ssh-rsa": paramiko.RSAKey, "ssh-ed25519": paramiko.Ed25519Key}.get(keytype, paramiko.ECDSAKey)
    return cls(data=data)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        local = self.request
        try:
            chan = self.server.ssh.get_transport().open_session()
            chan.exec_command(CMD)
        except Exception as e:
            err("channel", e)
            local.close()
            return

        def upstream():
            try:
                while True:
                    d = local.recv(CHUNK)
                    if not d:
                        break
                    chan.sendall(d)
            except Exception:
                pass
            try:
                chan.shutdown_write()
            except Exception:
                pass

        threading.Thread(target=upstream, daemon=True).start()
        try:
            while True:
                d = chan.recv(CHUNK)
                if not d:
                    break
                local.sendall(d)
        except Exception:
            pass
        finally:
            for c in (chan, local):
                try:
                    c.close()
                except Exception:
                    pass


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = False


def main():
    global _secret
    try:
        _secret = os.environ["LAB05_SSH_PASSWORD"]
        b64, keytype = os.environ["LAB05_SSH_HOSTKEY"], os.environ["LAB05_SSH_KEYTYPE"]
    except KeyError as e:
        print(f"ERROR missing env var {e.args[0]}", file=sys.stderr)
        return 2
    ssh = paramiko.SSHClient()
    try:
        ssh.get_host_keys().add(f"[{SSH_HOST}]:{SSH_PORT}", keytype, load_key(keytype, b64))
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, password=_secret,
                    look_for_keys=False, allow_agent=False, timeout=15)
        ssh.get_transport().set_keepalive(30)
    except Exception as e:
        err("ssh", e)
        ssh.close()
        return 1
    try:
        srv = Server(LOCAL, Handler)
    except Exception as e:
        err("listen", e)
        ssh.close()
        return 1
    srv.ssh = ssh
    print(f"READY http://{LOCAL[0]}:{LOCAL[1]}/", flush=True)
    try:
        srv.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
        ssh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
