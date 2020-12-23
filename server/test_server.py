import unittest
import mock
from utils import (
    COMMANDS,
    validateCommand,
    validateType,
    validateStringParameter,
    validateStringCharacters,
    validatePort,
)
from server import (
    handleUSER,
    handlePASS,
    handleTYPE,
    handleSYST,
    handlePORT,
    handleRETR,
    handleQUIT,
    handleNOOP,
)


class TestUtils(unittest.TestCase):
    def testValidateType(self):
        self.assertEqual(validateType("a"), True)
        self.assertEqual(validateType("A"), True)
        self.assertEqual(validateType("i"), True)
        self.assertEqual(validateType("I"), True)
        self.assertEqual(validateType("g"), False)
        self.assertEqual(validateType("gi"), False)
        self.assertEqual(validateType("ig"), False)

    def testValidateCommand(self):
        for c in COMMANDS:
            self.assertEqual(validateCommand(c), "")
            self.assertEqual(validateCommand(c.upper()), "")
        self.assertEqual(validateCommand("usr"), "502 Command not implemented.\r\n")
        self.assertEqual(
            validateCommand(""), "500 Syntax error, command unrecognized.\r\n"
        )
        self.assertEqual(validateCommand("user"), "")
        self.assertEqual(validateCommand("USER"), "")
        self.assertEqual(validateCommand("tet"), "502 Command not implemented.\r\n")
        self.assertEqual(validateCommand("test"), "502 Command not implemented.\r\n")
        self.assertEqual(
            validateCommand("areallylongcommand"),
            "500 Syntax error, command unrecognized.\r\n",
        )
        self.assertEqual(
            validateCommand(""), "500 Syntax error, command unrecognized.\r\n"
        )

    def testValidateStringParameter(self):
        self.assertEqual(validateStringParameter("string"), True)
        self.assertEqual(validateStringParameter(""), False)
        self.assertEqual(validateStringParameter(9000), False)

    def testValidateStringCharacters(self):
        self.assertEqual(validateStringCharacters("testing1!"), True)
        self.assertEqual(validateStringCharacters("TestInG1!"), True)
        self.assertEqual(
            validateStringCharacters(
                "!\"#$%&'()+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
            ),
            True,
        )
        self.assertEqual(validateStringCharacters("TestInG1*"), False)
        self.assertEqual(
            validateStringCharacters(
                "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
            ),
            False,
        )

    def testValidatePort(self):
        self.assertEqual(validatePort("152,23,81,126,31,64"), True)
        self.assertEqual(validatePort("270,23,81,126,31,64"), False)
        self.assertEqual(validatePort("-152,23,81,126,31,64"), False)
        self.assertEqual(validatePort("152,23,81,126,31"), False)
        self.assertEqual(validatePort("152,23,81,126,31,"), False)


class TestServer(unittest.TestCase):
    def testHandleUSER(self):
        self.assertEqual(handleUSER("nick"), "331 Guest access OK, send password.\r\n")
        self.assertEqual(handleUSER(""), "500 Syntax error, command unrecognized.\r\n")
        self.assertEqual(handleUSER("nick*"), "501 Syntax error in parameter.\r\n")

    def testHandlePASS(self):
        self.assertEqual(handlePASS("password"), "230 Guest login OK.\r\n")
        self.assertEqual(handlePASS(""), "501 Syntax error in parameter.\r\n")
        self.assertEqual(handleUSER("password*"), "501 Syntax error in parameter.\r\n")

    def testHandleTYPE(self):
        self.assertEqual(handleTYPE("i"), "200 Type set to I.\r\n")
        self.assertEqual(handleTYPE("I"), "200 Type set to I.\r\n")
        self.assertEqual(handleTYPE("a"), "200 Type set to A.\r\n")
        self.assertEqual(handleTYPE("A"), "200 Type set to A.\r\n")
        self.assertEqual(handleTYPE(""), "501 Syntax error in parameter.\r\n")
        self.assertEqual(handleTYPE("iminvalid"), "501 Syntax error in parameter.\r\n")

    def testHandlePORT(self):
        self.assertEqual(
            handlePORT("258,0,0,1,31,64"),
            "501 Syntax error in parameter.\r\n",
        )
        with mock.patch("socket.socket") as mock_socket:
            self.assertEqual(
                handlePORT("127,0,0,1,31,64"),
                "200 Port command successful (127.0.0.1,8000).\r\n",
            )
            mock_socket.return_value.connect.assert_called_with(("127.0.0.1", 8000))

        with mock.patch("socket.socket") as mock_socket:
            mock_socket.side_effect = Exception("")
            self.assertEqual(
                handlePORT("127,0,0,1,31,64"),
                "425 Can not open data connection.\r\n",
            )

    # TODO: Handle more cases with some more connected testing
    def testHandleRETR(self):
        self.assertEqual(handleRETR(""), "550 File not found or access denied.\r\n")
        self.assertEqual(
            handleRETR("invalid_file.txt"),
            "550 File not found or access denied.\r\n",
        )
        self.assertEqual(
            handleRETR("helper_file.txt"),
            "425 Can not open data connection.\r\n",
        )

    def testHandleSYST(self):
        self.assertEqual(
            handleSYST(""),
            "215 UNIX Type: L8.\r\n",
        )
        self.assertEqual(handleSYST("parameter"), "501 Syntax error in parameter.\r\n")

    def testHandleQUIT(self):
        self.assertEqual(handleQUIT(""), "221 Goodbye.\r\n")
        self.assertEqual(handleQUIT("parameter"), "501 Syntax error in parameter.\r\n")

    def testHandleNOOP(self):
        self.assertEqual(handleNOOP(""), "200 Command OK.\r\n")
        self.assertEqual(handleNOOP("parameter"), "501 Syntax error in parameter.\r\n")
