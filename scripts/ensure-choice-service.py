#!/usr/bin/env python3
"""Start the local-only grill-choice server when it is not already running."""
import socket
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print("Usage: ensure-choice-service.py <root_dir> <port>", file=sys.stderr)
        raise SystemExit(2)

    root = Path(sys.argv[1]).expanduser().resolve()
    port = int(sys.argv[2])
    script = (Path(__file__).resolve().parent / "choice-server.py").resolve()
    if not root.is_dir():
        print(f"archive directory not found: {root}", file=sys.stderr)
        raise SystemExit(2)

    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            print(f"grill-choice already running at http://127.0.0.1:{port}/")
            return

    log = (root / ".grill-choice.log").open("a", encoding="utf-8")
    subprocess.Popen(
        [sys.executable, str(script), str(root), str(port)],
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    print(f"grill-choice started at http://127.0.0.1:{port}/")


if __name__ == "__main__":
    main()
