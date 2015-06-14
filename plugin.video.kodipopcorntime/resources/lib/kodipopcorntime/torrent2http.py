def ensure_exec_perms(file_):
    st = os.stat(file_)
    os.chmod(file_, st.st_mode | stat.S_IEXEC)
    return file_

import os, sys, stat, subprocess, socket
from kodipopcorntime.common import RESOURCES_PATH, PLATFORM

def get_torrent2http_binary():
    binary = "torrent2http%s" % (PLATFORM["os"] == "windows" and ".exe" or "")

    platform = PLATFORM.copy()
    if platform["os"] == "darwin": # 64 bits anyway on Darwin
        platform["arch"] = "x64"
    elif platform["os"] == "windows": # 32 bits anyway on Windows
        platform["arch"] = "x86"

    binary_dir = os.path.join(RESOURCES_PATH, "bin", "%(os)s_%(arch)s" % platform)
    binary_path = os.path.join(binary_dir, binary)

    return binary_dir, ensure_exec_perms(binary_path)


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start(**kwargs):
    torrent2http_dir, torrent2http_bin = get_torrent2http_binary()
    args = [torrent2http_bin]
    bind_port = find_free_port()
    kwargs["bind"] = ":%d" % bind_port

    for k, v in kwargs.items():
        args.append("--%s" % k)
        if v:
            args.append(v)

    # Needed because torrent2http is vendored with Boost and libtorrent-rasterbar
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = torrent2http_dir
    env["DYLD_LIBRARY_PATH"] = torrent2http_dir

    kwargs = {
        "cwd": torrent2http_dir,
        "env": env,
    }
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= 1
        si.wShowWindow = 0
        kwargs["startupinfo"] = si
    proc = subprocess.Popen(args, **kwargs)
    proc.bind_address = "localhost:%d" % bind_port
    def proc_close():
        if not proc.poll():
            urllib2.urlopen("http://%s/shutdown" % proc.bind_address)
    proc.close = proc_close
    return proc
