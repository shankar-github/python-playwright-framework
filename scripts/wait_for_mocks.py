#!/usr/bin/env python3
"""Wait for mock servers to become healthy before running tests."""
import sys
import time
import urllib.error
import urllib.request


def wait_for_url(url: str, timeout_seconds: float = 30.0, poll_interval: float = 0.25) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
        time.sleep(poll_interval)
    raise TimeoutError(f"Timed out waiting for {url}: {last_error}")


def main():
    targets = sys.argv[1:] or [
        "http://localhost:8080/health",
        "http://localhost:3000/health",
    ]
    for target in targets:
        wait_for_url(target)
        print(f"Ready: {target}")


if __name__ == "__main__":
    try:
        main()
    except TimeoutError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
