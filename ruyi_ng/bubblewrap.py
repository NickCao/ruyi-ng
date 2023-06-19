from subprocess import Popen
from shutil import which
import os, json
from . import subordinate


def bwrap(*args):
    info_fds = os.pipe()
    user_fds = os.pipe()

    proc = Popen(
        [
            which("bwrap"),
            "--unshare-user",
            "--userns-block-fd",
            "%i" % user_fds[0],
            "--info-fd",
            "%i" % info_fds[1],
            *args,
        ],
        pass_fds=(user_fds[0], info_fds[1]),
    )

    os.close(info_fds[1])
    os.close(user_fds[0])

    data = json.load(os.fdopen(info_fds[0]))
    subordinate.map(data["child-pid"])
    os.write(user_fds[1], b"1")

    proc.wait()


def activate(root, *cmd):
    # fmt: off
    bwrap(
        # common bind mounts
        "--bind", root   , "/"    ,
        "--bind", "/home", "/home",
        # nix specific bind mounts
        "--ro-bind-try", "/nix/store" , "/nix/store" ,
        "--ro-bind-try", "/run/binfmt", "/run/binfmt",
        # niches
        "--ro-bind-try", "/etc/resolv.conf", "/etc/resolv.conf",
        # special file systems
        "--proc" , "/proc",
        "--dev"  , "/dev" ,
        "--tmpfs", "/tmp" ,
        "--chmod", "1777", "/tmp",
        # privileges
        "--cap-add", "ALL",
        # environment
        "--unsetenv", "PATH",
        # command
        *cmd
    )
    # fmt: on
