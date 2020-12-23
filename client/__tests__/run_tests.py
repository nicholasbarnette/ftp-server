import os
import subprocess
import time
import difflib
from config import SERVER_PORT, CLIENT_PORT

# Import Tests
from client_tests import CLIENT_TESTS


def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """
    expected = expected.replace("\r", "").splitlines(1)
    actual = actual.replace("\r", "").splitlines(1)

    diff = difflib.unified_diff(expected, actual)

    return "".join(diff)


def main():
    failed = 0
    client = None
    server = None
    try:
        print("Setting up...\n\n")
        server = subprocess.Popen(
            "python -u ./server/index.py %s" % str(SERVER_PORT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1)

        for test in CLIENT_TESTS:
            # Open a new client
            client = subprocess.Popen(
                "python -u ./client/index.py %s" % str(CLIENT_PORT),
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(0.5)

            print("Running test [client/%s]: %s" % (test["name"], test["description"]))
            data = client.communicate(input=test["input"].encode())[0]
            dif = _unidiff_output(test["output"], data.decode())
            if len(dif) > 0:
                failed += 1
                print(
                    "Error in [client/%s]: %s\n%s"
                    % (test["description"], test["output"], dif)
                )
        print("\n")

    except Exception as e:
        print(str(e) + "\n")
    finally:
        if failed > 0:
            print("%d tests failed" % failed)

        print("Cleaning up...")
        client.kill()
        server.kill()


main()