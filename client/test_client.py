import unittest
import mock
import socket
import time
import subprocess
from utils import (
    validateString,
    validatePort,
    validateHost,
    validateIP,
    validateCommand,
    validateResponseCode,
    convertPort,
)
from client import COMMANDS, parseCommand


class TestUtils(unittest.TestCase):
    def testValidateString(self):
        self.assertEqual(
            validateString(
                "!\"#$%&'()+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
            ),
            True,
        )

    def testValidatePort(self):
        self.assertEqual(
            validatePort("0"),
            True,
        )
        self.assertEqual(
            validatePort("65535"),
            True,
        )
        self.assertEqual(
            validatePort("8080"),
            True,
        )
        self.assertEqual(
            validatePort("-10"),
            False,
        )
        self.assertEqual(
            validatePort("70000"),
            False,
        )
        self.assertEqual(
            validatePort("invalid"),
            False,
        )
        self.assertEqual(
            validatePort("0800"),
            False,
        )

    def testValidateHost(self):
        self.assertEqual(
            validateHost("127.0.0.1"),
            True,
        )
        self.assertEqual(
            validateHost("192.168.1.1"),
            True,
        )
        self.assertEqual(
            validateHost("www.google.com"),
            True,
        )
        self.assertEqual(
            validateHost("google"),
            True,
        )
        self.assertEqual(
            validateHost("www.google."),
            False,
        )
        self.assertEqual(
            validateHost("270.168.1.1"),
            False,
        )

    def testValidateIP(self):
        self.assertEqual(
            validateIP("127.0.0.1"),
            True,
        )
        self.assertEqual(
            validateIP("192.168.1.1"),
            True,
        )
        self.assertEqual(
            validateIP("127.0.0.1.1"),
            False,
        )
        self.assertEqual(
            validateIP("www.google.com"),
            False,
        )
        self.assertEqual(
            validateIP("270.168.1.1"),
            False,
        )

    def testValidateCommand(self):
        for c in COMMANDS:
            self.assertEqual(
                validateCommand(c.upper()),
                True,
            )
            self.assertEqual(
                validateCommand(c.lower()),
                True,
            )
        self.assertEqual(
            validateCommand("CoNnEcT"),
            True,
        )
        self.assertEqual(
            validateCommand("cnct"),
            False,
        )
        self.assertEqual(
            validateCommand("post"),
            False,
        )
        self.assertEqual(
            validateCommand(""),
            False,
        )

    def testValidateResponseCode(self):
        self.assertEqual(
            validateResponseCode("100"),
            True,
        )
        self.assertEqual(
            validateResponseCode("599"),
            True,
        )
        self.assertEqual(
            validateResponseCode("invalid"),
            False,
        )
        self.assertEqual(
            validateResponseCode("90"),
            False,
        )
        self.assertEqual(
            validateResponseCode("0500"),
            False,
        )
        self.assertEqual(
            validateResponseCode("700"),
            False,
        )

    def testConvertPort(self):
        self.assertEqual(
            convertPort("127.0.0.1", "8000"),
            "127,0,0,1,31,64",
        )


class TestClient(unittest.TestCase):
    def testParseCommand(self):
        self.assertEqual(
            parseCommand(["CONNECT", "127.0.0.1", "8000"]),
            None,
        )
        self.assertEqual(
            parseCommand(["CNT"]),
            False,
        )
        self.assertEqual(
            parseCommand(["CONNECT", "localhost", "8000"]),
            False,
        )
        self.assertEqual(
            parseCommand(["CONNECT", "localhost", "70000"]),
            False,
        )
        self.assertEqual(
            parseCommand(["GET", "invalid.txt"]),
            False,
        )
        self.assertEqual(
            parseCommand(["QUIT", "parameter"]),
            False,
        )
        self.assertEqual(
            parseCommand(["QUIT"]),
            False,
        )


class TestClientConnected(unittest.TestCase):
    def setUp(self):
        try:
            self.port = 8003
            self.server = subprocess.Popen(
                "python -u ../server/index.py %s" % str(self.port),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            time.sleep(0.5)
        except Exception as e:
            pass

    def tearDown(self):
        try:
            self.server.kill()
        except Exception:
            pass

    def testParseCommand(self):
        self.assertEqual(
            parseCommand(["CONNECT", "127.0.0.1", str(self.port)]),
            None,
        )
        self.assertEqual(
            parseCommand(["QUIT"]),
            True,
        )
