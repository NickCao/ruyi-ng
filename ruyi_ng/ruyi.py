#!/usr/bin/env python3

import click
from subprocess import run
from pathlib import Path
from shutil import which
import time
import os, select, subprocess, sys, json

OSTREE = which("ostree")
OSTREE_EXT = which("ostree-ext-cli")
BWRAP = which("bwrap")
RUYI = Path.home() / "Downloads" / "ruyi-root"
REPO = RUYI / "repo"
WORK = RUYI / "work"
REMOTE = "120.46.154.124:8080"


@click.group()
def cli():
    pass


@click.command()
def init():
    REPO.mkdir(parents=True)
    WORK.mkdir(parents=True)
    run([OSTREE, "init", "--repo", REPO, "--mode", "bare-user"])


@click.command()
def refs():
    run([OSTREE, "refs", "--repo", REPO])


@click.command()
@click.argument("name")
@click.argument("ref")
def pull(name, ref):
    run([OSTREE_EXT, "container", "unencapsulate", "--repo", REPO, "--write-ref", name, f"ostree-unverified-image:registry:{REMOTE}/library/{ref}"])


@click.command()
@click.argument("name")
@click.argument("workdir")
def checkout(name, workdir):
    run([OSTREE, "checkout", "--repo", REPO, "--user-mode", name, WORK / workdir])


@click.command()
@click.argument("workdir")
def activate(workdir):
    pipe_info = os.pipe()
    userns_block = os.pipe()

    pid = os.fork()

    if pid != 0:
        os.close(pipe_info[1])
        os.close(userns_block[0])

        select.select([pipe_info[0]], [], [])

        data = json.load(os.fdopen(pipe_info[0]))
        child_pid = str(data['child-pid'])

        subprocess.call([
                         "newuidmap", child_pid,
                         "0", str(os.getuid()), "1",
                         "1", "100000",         "65536",
                       ])
        subprocess.call([
                         "newgidmap", child_pid,
                         "0", str(os.getgid()), "1",
                         "1", "100000",         "65536",
                       ])

        os.write(userns_block[1], b'1')

        os.waitpid(pid, 0)
    else:
        os.close(pipe_info[0])
        os.close(userns_block[1])

        os.set_inheritable(pipe_info[1], True)
        os.set_inheritable(userns_block[0], True)

        # os.dup2(sys.stdin.fileno(), 0)
        # os.dup2(sys.stdout.fileno(), 1)

        print(os.execlp(
            BWRAP,
            BWRAP,
            "--unshare-user",
            "--userns-block-fd", "%i" % userns_block[0],
            "--info-fd", "%i" % pipe_info[1],
            "--uid",
            "0",
            "--gid",
            "0",
            "--cap-add",
            "ALL",
            "--bind",
            WORK / workdir,
            "/",
            "--bind",
            "/home",
            "/home",
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--tmpfs",
            "/tmp",
            "--chmod",
            "1777",
            "/tmp",
            "--ro-bind-try", "/nix", "/nix",
            "--ro-bind-try", "/run/binfmt", "/run/binfmt",
            "--ro-bind-try", "/etc/resolv.conf", "/etc/resolv.conf",
            "--unsetenv",
            "PATH",
            "/bin/sh"
        ))


@click.command()
@click.argument("workdir")
@click.argument("name")
def commit(workdir, name):
    run([OSTREE, "commit", "--repo", REPO, "--branch", name, WORK / workdir])


cli.add_command(init)
cli.add_command(refs)
cli.add_command(pull)
cli.add_command(checkout)
cli.add_command(activate)
cli.add_command(commit)

def entrypoint():
    cli()
