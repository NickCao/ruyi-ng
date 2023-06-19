import csv
import subprocess
import os


def load(file, login):
    with open(file) as f:
        reader = csv.reader(f, delimiter=":")
        return [(row[1], row[2]) for row in reader if row[0] == login]


def map(pid):
    login = os.getlogin()

    subuid = load("/etc/subuid", login)
    subgid = load("/etc/subgid", login)

    subprocess.run(
        [
            "newuidmap",
            pid,
            "0",
            str(os.getuid()),
            "1",
            "1",
            subuid[0][0],
            subuid[0][1],
        ],
        check=True,
    )

    subprocess.run(
        [
            "newgidmap",
            pid,
            "0",
            str(os.getgid()),
            "1",
            "1",
            subgid[0][0],
            subgid[0][1],
        ],
        check=True,
    )
